from core.models import Track
from core.api_schemas import ErrorResponse
from core.serializers import TrackNameOnlyMSGSerializer
from core.permissions import NinjaIsTechnical, NinjaIsTechnicalOrMember
from notifications.tasks import send_notification_to_track_members, send_notification_to_user

from member.models import Member, ReciviedTask
from member.caches import member_profile_cache_key
from member.api_schemas import RecivedTaskMember, TaskResponse
from member.serializers import MemberTechnicalMSGSerializer, RecivedTaskMSGSerializer

from .models import MemberTechEditType, Task
from .serializers import TaskMSGSerializer
from .api_schemas import (
    TechnicalMembersTasksUpdateRequest,
    TechnicalMembersResponse,
    TaskAlreadyExistsError,
    TaskCreateRequest,
    TaskSignRequest,
)
from .caches import (
    members_by_technicals_cache_key,
    tasks_from_memebrs_cache_key,
    technical_tasks_cache_key,
    task_view_cache_key,
)

from utils import DEFAULT_CACHE_DURATION, JSON_CONTENT_TYPE, serializer_encoder
from ninja_extra import api_controller, route, status
from ninja_extra.exceptions import NotFound

from django.http import HttpRequest, HttpResponse
from django.db.models.functions import Coalesce
from django.shortcuts import aget_object_or_404
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.db.models import (
    ExpressionWrapper,
    BooleanField,
    IntegerField,
    Prefetch,
    Subquery,
    OuterRef,
    Count,
    Q,
)


@api_controller("/technical/tasks", tags=["Technical"], permissions=[NinjaIsTechnical])
class TechnicalTasksController:
    
    @route.get("/", response={200: list[TaskResponse]})
    async def get_all(self, request: HttpRequest):
        TRACK: Track = request.user.track # type: ignore
        if cached := await cache.aget(technical_tasks_cache_key(TRACK.name)):
            return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)
        
        sub = Subquery(
            ReciviedTask.objects
            .filter(
                task_id=OuterRef('pk'), 
                track=TRACK, 
                signed=False
            )
            .values("task_id")
            .annotate(cnt=Count('id'))
            .values('cnt'),
            output_field=IntegerField()
        )
        
        data = (
            Task.objects
            .filter(track=TRACK)
            .annotate(
                expired=ExpressionWrapper(
                    Q(expires_at__lte=timezone.now()), 
                    output_field=BooleanField()
                ),
                unsigned_tasks_count=Coalesce(sub, 0)
            )
            .values("id", "task_number", "created_at", "expires_at", "description", "expired", "unsigned_tasks_count")
        )
        
        encoded_data = serializer_encoder.encode(await TaskMSGSerializer.afrom_queryset_values(data))
        await cache.aset(technical_tasks_cache_key(TRACK.name), encoded_data, DEFAULT_CACHE_DURATION)
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

    @route.post("/", response={201: TaskResponse, 400: TaskAlreadyExistsError})
    async def add_task(self, request: HttpRequest, payload: TaskCreateRequest):
        TRACK: Track = request.user.track # type: ignore
        
        if await Task.objects.filter(track=TRACK, task_number=payload.task_number).aexists():
            return status.HTTP_400_BAD_REQUEST, {"task_number": "This task number already exists"}
            
        created_task = await Task.objects.acreate(
            task_number = payload.task_number,
            expires_at = payload.expires_at,
            description = payload.description,
            track=TRACK
        )
        encoded_data = TaskMSGSerializer.from_model(created_task).encode()
        
        send_notification_to_track_members(
            track_id=TRACK.pk,
            title="New Task!",
            body=f"Task {created_task.task_number} is now avilable",
            url=f"/member/{TRACK.name}/tasks/{created_task.pk}"
        )
        
        cache.delete(technical_tasks_cache_key(TRACK.name))
        cache.delete_pattern(f"member_tasks:t{TRACK.name}*") # type: ignore
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE, status=status.HTTP_201_CREATED)
    
    @route.get("/{task_id}/", response={200: TaskResponse}, permissions=[NinjaIsTechnicalOrMember])
    async def get_one(self, task_id: int):
        CACHE_KEY = task_view_cache_key(task_id)
        if cached := await cache.aget(CACHE_KEY):
            return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)

        data = await aget_object_or_404(
            Task.objects.annotate(
                expired=ExpressionWrapper(
                    Q(expires_at__lte=timezone.now()), output_field=BooleanField()
                )
            )
            .values("id", "task_number", "description", "created_at", "expires_at", "expired"), # type: ignore
            id=task_id,
        )
        
        encoded_data = serializer_encoder.encode(
            TaskMSGSerializer.from_model_values(data)
        )
        await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)
    
    @route.put('/{task_id}/', response={204: None, 400: ErrorResponse})
    async def update_task(self, request: HttpRequest, task_id: int, payload: TaskCreateRequest):
        TRACK: Track = request.user.track # type: ignore
        data_to_update: set[str] = set()

        TASK = await aget_object_or_404(Task, id=task_id)
        
        if payload.task_number:
            data_to_update.add("task_number")
            TASK.task_number = payload.task_number

        if payload.expires_at:
            data_to_update.add("expires_at")
            TASK.expires_at = payload.expires_at

        if payload.description:
            data_to_update.add("description")
            TASK.description = payload.description

        if not data_to_update:
            return status.HTTP_400_BAD_REQUEST, {"details": "nothing to update"}
        
        try:
            await TASK.asave(update_fields=data_to_update)
            await cache.adelete_many(
                [
                    task_view_cache_key(task_id),
                    technical_tasks_cache_key(TRACK.name)
                ]
            )
            send_notification_to_track_members(
                track_id=TRACK.pk,
                title="Task Update",
                body=f"Task {TASK.task_number} has been updated",
                url=f"/member/{TRACK.name}/tasks/{task_id}"
            )
            return status.HTTP_204_NO_CONTENT, {}
        except Exception as e:
            return status.HTTP_400_BAD_REQUEST, {"details": repr(e)}
        
    @route.delete('/{task_id}/', response={204: None, 404: ErrorResponse})
    async def delete_task(self, request: HttpRequest, task_id: int):
        
        @sync_to_async
        def safe_transaction() -> None:
            with transaction.atomic():
                count, _ = Task.objects.filter(id=task_id).delete()
                if count == 0:
                    raise NotFound("no task found")
                
        await safe_transaction()
        await cache.adelete_many(
            [
                task_view_cache_key(task_id),
                technical_tasks_cache_key(request.user.track.name), # type: ignore
            ]
        )
        return status.HTTP_204_NO_CONTENT, {}
    
    @route.get("/{task_id}/recived/", response={200: list[RecivedTaskMember]})
    async def get_recived_tasks_from_members(self, request: HttpRequest, task_id: int):
        track: Track = request.user.track # type: ignore
        
        CACHE_KEY = tasks_from_memebrs_cache_key(track.name, task_id)
        if cached := await cache.aget(CACHE_KEY):
            return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)

        tasks = (
            ReciviedTask.objects
            .select_related("track", "task", "member", "member__bdaya_user", 'signed_by')
            .prefetch_related("files")
            .defer(
                "task__track",
                "member__collage_code",
                "member__bonus",
                "member__track",
                "member__joined_at",
                "member__status",
            )
            .filter(
                track=track,
                task_id=task_id,
                signed=False
            )
        )
        
        encoded_data = serializer_encoder.encode(await RecivedTaskMSGSerializer.afrom_queryset(tasks))
        await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)
    
    @route.post("/{task_id}/recived/", response={204: None, 400: ErrorResponse})
    async def sign_task(self, request: HttpRequest, task_id: int, payload: TaskSignRequest):
        track: Track = request.user.track # type: ignore
        recived_task = await aget_object_or_404(ReciviedTask.objects.select_related('task', 'member', 'member__bdaya_user'), id=task_id, track=track)
        
        try:
            await ReciviedTask.objects.filter(id=recived_task.pk).aupdate(
                degree=payload.degree,
                technical_notes=payload.technical_notes,
                signed=True,
                signed_by=request.user
            )
            
            await send_notification_to_user(
                user_id=recived_task.member.bdaya_user.pk,
                title=f"Task {recived_task.task.task_number} Signed",
                body=payload.technical_notes,
                url=f"/profile/{recived_task.member.code}"
            )
            
            await cache.adelete_many(
                [
                    tasks_from_memebrs_cache_key(track.name, recived_task.task.pk),
                    member_profile_cache_key(recived_task.member.code),
                    technical_tasks_cache_key(track.name)
                ]
            )
        except Exception as e:
            return status.HTTP_400_BAD_REQUEST, {"details": repr(e)}
        
        return status.HTTP_204_NO_CONTENT, {}
    

@api_controller("/technical", tags=["Technical"], permissions=[NinjaIsTechnical])
class TechnicalMembersController:
    
    @route.get("/members/{track_name}/with-tasks/", response={200: list[TechnicalMembersResponse], 403: ErrorResponse})
    async def get_members(self, request: HttpRequest, track_name: str):
        TRACK = track_name.replace("%20", " ")
        track_obj: Track = request.user.track # type: ignore
        
        if request.user.is_technical and track_obj.name != TRACK: # type: ignore
            return status.HTTP_403_FORBIDDEN, {"details": f"Not Your Track {request.user.username}"}

        CACHE_KEY = members_by_technicals_cache_key(track_name)
        if cached_data := await cache.aget(CACHE_KEY):
            return HttpResponse(cached_data, content_type=JSON_CONTENT_TYPE)
        
        track_serialized = TrackNameOnlyMSGSerializer.from_model(track_obj)

        members = (
            Member.objects
            .prefetch_related(
                Prefetch(
                    "tasks_sent",
                    ReciviedTask.objects.select_related('task', 'signed_by'),
                    "prefetched_tasks"
                )
            )
            .select_related("bdaya_user")
            .order_by("joined_at")
            .filter(track=track_obj)
        )
        
        data = await MemberTechnicalMSGSerializer.afrom_queryset_with_track(members, track_serialized)
        encoded_data = serializer_encoder.encode(data)
        await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)
    
    @route.put("/members/{track_name}/with-tasks/", response={204: None, 404: ErrorResponse})
    async def update_member_task(self, request: HttpRequest, track_name: str, payload: TechnicalMembersTasksUpdateRequest):
        recivied_task = await aget_object_or_404(ReciviedTask.objects.only("id", "notes", "degree"), task_id=payload.task_id, member__code=payload.code)
        
        match payload.field:
            case MemberTechEditType.NOTES:
                recivied_task.notes = str(payload.value)
            case MemberTechEditType.DEGREE:
                recivied_task.degree = int(payload.value)
        
        recivied_task.signed_by = request.user # type: ignore
                
        await recivied_task.asave()
        cache.delete(members_by_technicals_cache_key(track_name))
        return status.HTTP_204_NO_CONTENT, {}

