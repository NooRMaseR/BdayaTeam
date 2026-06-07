from core.models import BdayaUser, Track
from core.serializers import TrackNameOnlyMSGSerializer
from core.permissions import get_tech_user, get_tech_or_member_user
from notifications.tasks import send_notification_to_track_members, send_notification_to_user

from member.serializers import MemberTechnicalMSGSerializer, RecivedTaskMSGSerializer
from member.models import AllowedTrackFileExtention, Member, ReciviedTask
from member.caches import member_profile_cache_key

from .models import MemberTechEditType, Task, TaskImage
from .serializers import TaskMSGSerializer, TrackExtenstionsSerializer
from .api_schemas import (
    TaskCreateRequestMSG,
    TaskSignRequestMSG,
    TechnicalMembersTasksUpdateRequestMSG,
    TrackExtensionsRequestMSG,
)
from .caches import (
    extenstions_cache_key,
    members_by_technicals_cache_key,
    tasks_from_memebrs_cache_key,
    technical_tasks_cache_key,
    task_view_cache_key,
)

from utils import DEFAULT_CACHE_DURATION, JSON_CONTENT_TYPE, serializer_encoder
from typing import Annotated

from django.db.models.functions import Coalesce
from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.conf import settings
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
from django_bolt.exceptions import NotFound, BadRequest, Forbidden
from django_bolt import BoltAPI, Depends, Response, status
from django_bolt.param_functions import Form

bolt = BoltAPI(
    prefix="/api/technical/",
    trailing_slash="append",
    validate_response=False,
    django_middleware=settings.BOLT_MIDDLEWARE
)


@bolt.get("/tasks/", response_model=list[TaskMSGSerializer])
async def tech_get_all(user: BdayaUser = Depends(get_tech_user)): # type: ignore
    "get all created tasks"
    
    TRACK: Track = user.track # type: ignore
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
        .prefetch_related('images')
        .annotate(
            expired=ExpressionWrapper(
                Q(expires_at__lte=timezone.now()), 
                output_field=BooleanField()
            ),
            unsigned_tasks_count=Coalesce(sub, 0)
        )
    )
    
    encoded_data = serializer_encoder.encode(await TaskMSGSerializer.afrom_queryset(data))
    await cache.aset(technical_tasks_cache_key(TRACK.name), encoded_data, DEFAULT_CACHE_DURATION)
    return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

@bolt.post("/tasks/", status_code=201, response_model=TaskMSGSerializer)
async def add_task(payload: Annotated[TaskCreateRequestMSG, Form()], user: BdayaUser = Depends(get_tech_user)): # type: ignore
    "create a task"
    
    TRACK: Track = user.track # type: ignore
    
    if await Task.objects.filter(track=TRACK, task_number=payload.task_number).aexists():
        return Response({"task_number": "This task number already exists"}, status.HTTP_400_BAD_REQUEST)
    
    @sync_to_async
    def perform_safe_create() -> Task:
        with transaction.atomic():
            created_task = Task.objects.create(
                task_number = payload.task_number,
                expires_at = payload.expires_at,
                description = payload.description,
                track=TRACK,
                links=payload.links,
                can_recive_tasks_after_expiration=payload.can_recive_tasks_after_expiration
            )
            task_images = (TaskImage(task=created_task, image=image.file) for image in payload.images)
            TaskImage.objects.bulk_create(task_images)
            return created_task
    
    try:
        created_task = await perform_safe_create()
    except:
        raise BadRequest(detail="error while saving")
    
    send_notification_to_track_members(
        track_id=TRACK.pk,
        title="New Task!",
        body=f"Task {created_task.task_number} is now avilable",
        url=f"/member/{TRACK.name}/tasks/{created_task.pk}"
    )
    
    cache.delete(technical_tasks_cache_key(TRACK.name))
    cache.delete_pattern(f"member_tasks:t{TRACK.name}*") # type: ignore
    return Response(status_code=status.HTTP_201_CREATED)

@bolt.get("/tasks/{task_id}/", response_model=TaskMSGSerializer)
async def get_one_task(task_id: int, user = Depends(get_tech_or_member_user)):
    "get one task"
    
    CACHE_KEY = task_view_cache_key(task_id)
    if cached := await cache.aget(CACHE_KEY):
        return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)

    try:
        data = await (
            Task.objects.annotate(
                expired=ExpressionWrapper(
                    Q(expires_at__lte=timezone.now()), output_field=BooleanField()
                )
            )
            .prefetch_related('images')
            .aget(id=task_id)
        )
    except Task.DoesNotExist:
        raise NotFound(detail=f"Task with id {task_id} does not exists")
    
    encoded_data = serializer_encoder.encode(
        TaskMSGSerializer.from_model(data)
    )
    await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)


@bolt.put('/tasks/{task_id}/', status_code=204)
async def update_task(task_id: int, payload: Annotated[TaskCreateRequestMSG, Form()], user: BdayaUser = Depends(get_tech_user)): # type: ignore
    "update task info"
    
    TRACK: Track = user.track # type: ignore
    data_to_update: set[str] = set()

    try:
        TASK = await Task.objects.aget(id=task_id)
    except Task.DoesNotExist:
        raise NotFound(detail=f"Task with id {task_id} does not exists")
    
    if payload.task_number:
        TASK.task_number = payload.task_number
        data_to_update.add("task_number")

    if payload.expires_at:
        TASK.expires_at = payload.expires_at
        data_to_update.add("expires_at")

    if payload.description:
        TASK.description = payload.description
        data_to_update.add("description")

    if payload.images:
        task_images = (TaskImage(task=TASK, image=image.file) for image in payload.images)
        await TaskImage.objects.filter(task=TASK).adelete()
        await TaskImage.objects.abulk_create(task_images)

    if payload.links:
        TASK.links = payload.links # type: ignore
        data_to_update.add("links")
    
    if payload.can_recive_tasks_after_expiration != TASK.can_recive_tasks_after_expiration:
        TASK.can_recive_tasks_after_expiration = payload.can_recive_tasks_after_expiration
        data_to_update.add("can_recive_tasks_after_expiration")

    if not data_to_update:
        raise BadRequest(detail="nothing to update")
    
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
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        raise BadRequest(detail=repr(e))

@bolt.delete('/tasks/{task_id}/', status_code=204)
async def delete_task(task_id: int, user: BdayaUser = Depends(get_tech_user)): # type: ignore
    """delete task
    
    delete a task and all sent tasks to this task
    """
    
    @sync_to_async
    def safe_transaction() -> None:
        with transaction.atomic():
            count, _ = Task.objects.filter(id=task_id).delete()
            if count == 0:
                raise NotFound(detail=f"Task with id {task_id} does not exists")
            
    await safe_transaction()
    await cache.adelete_many(
        [
            task_view_cache_key(task_id),
            technical_tasks_cache_key(user.track.name), # type: ignore
        ]
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.get("/tasks/{task_id}/recived/", response_model=list[RecivedTaskMSGSerializer])
async def get_recived_tasks_from_members(task_id: int, user: BdayaUser = Depends(get_tech_user)): # type: ignore
    "get recived tasks from members"
    
    track: Track = user.track # type: ignore
    
    CACHE_KEY = tasks_from_memebrs_cache_key(track.name, task_id)
    if cached := await cache.aget(CACHE_KEY):
        return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)

    tasks = (
        ReciviedTask.objects
        .select_related("track", "task", "member", "member__bdaya_user", 'signed_by')
        .prefetch_related("files", 'task__images')
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

@bolt.post("/tasks/{task_id}/recived/", status_code=204)
async def sign_task(task_id: int, payload: TaskSignRequestMSG, user: BdayaUser = Depends(get_tech_user)): # type: ignore
    "sign a task with a `degree` and `message`"
    
    track: Track = user.track # type: ignore
    try:
        recived_task = await (
            ReciviedTask.objects
            .select_related('task', 'member', 'member__bdaya_user')
            .aget(id=task_id, track=track)
        )
    except ReciviedTask.DoesNotExist:
        raise NotFound(detail=f"Recived Task with id {task_id} does not exists")
    
    try:
        await ReciviedTask.objects.filter(id=recived_task.pk).aupdate(
            degree=payload.degree,
            technical_notes=payload.technical_notes,
            signed=True,
            signed_by=user
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
        raise BadRequest(detail=repr(e))
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@bolt.get("/members/{track_name}/with-tasks/", response_model=list[MemberTechnicalMSGSerializer])
async def get_members(track_name: str, user: BdayaUser = Depends(get_tech_user)): # type: ignore
    "get all track members with their sent tasks"
    
    TRACK = track_name.replace("%20", " ")
    track_obj: Track = user.track # type: ignore
    
    if user.is_technical and track_obj.name != TRACK: # type: ignore
        raise Forbidden(detail=f"Not Your Track {user.username}")

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

@bolt.put("/members/{track_name}/with-tasks/", status_code=204)
async def update_member_task(track_name: str, payload: TechnicalMembersTasksUpdateRequestMSG, user: BdayaUser = Depends(get_tech_user)): # type: ignore
    "update a reviewed task"
    
    try:
        recivied_task = await (
            ReciviedTask.objects
            .only("id", "notes", "degree")
            .aget(task_id=payload.task_id, member__code=payload.code)
        )
    except ReciviedTask.DoesNotExist:
        raise NotFound(detail=f"Recived task with id {payload.task_id} does not exists")
    
    match payload.field:
        case MemberTechEditType.NOTES:
            recivied_task.notes = str(payload.value)
        case MemberTechEditType.DEGREE:
            recivied_task.degree = int(payload.value)
    
    recivied_task.signed_by = user # type: ignore
            
    await recivied_task.asave()
    cache.delete(members_by_technicals_cache_key(track_name))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@bolt.get("/extension/", response_model=TrackExtenstionsSerializer)
async def get_extensions(user: BdayaUser = Depends(get_tech_or_member_user)): # type: ignore
    TRACK: Track = user.track # type: ignore
    CACHE_KEY = extenstions_cache_key(TRACK.name)
    
    if cached_data:=await cache.aget(CACHE_KEY):
        return HttpResponse(cached_data, content_type=JSON_CONTENT_TYPE)
    
    try:
        exts = await AllowedTrackFileExtention.objects.only("extensions").aget(track=TRACK)
    except AllowedTrackFileExtention.DoesNotExist:
        raise BadRequest(detail=f"no extensions found for track {TRACK.name}")
    
    encoded_data = TrackExtenstionsSerializer(track=TrackNameOnlyMSGSerializer.from_model(TRACK), extensions=exts.extensions).encode()
    await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)


@bolt.put("/extension/", status_code=204)
async def get_extensions(payload: TrackExtensionsRequestMSG, user: BdayaUser = Depends(get_tech_user)): # type: ignore
    TRACK: Track = user.track # type: ignore
    CACHE_KEY = extenstions_cache_key(TRACK.name)
    
    extensions_lowerd = [x.lower() for x in payload.extensions]
    
    for i, ext in enumerate(extensions_lowerd):
        if ext == 'jpeg':
            extensions_lowerd[i] = "jpg"
    
    extensions_lowerd = list(set(extensions_lowerd))
    
    try:
        await AllowedTrackFileExtention.objects.filter(track=TRACK).aupdate_or_create(track=TRACK, defaults={"extensions":extensions_lowerd})
    except:
        raise BadRequest(detail=f"error when updating the extensions")
    
    cache.delete(CACHE_KEY)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

