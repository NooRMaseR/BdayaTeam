from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest, HttpResponse
from django.db import IntegrityError, transaction
from django.shortcuts import aget_object_or_404
from django.db.models.functions import Coalesce
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.utils import timezone
from django.db.models import (
    PositiveSmallIntegerField,
    ExpressionWrapper,
    BooleanField,
    Prefetch,
    Subquery,
    OuterRef,
    Count,
    Q,
    F,
)

from ninja_extra import route, api_controller, status
from ninja_extra.permissions import IsAuthenticated
from ninja import File, Form, UploadedFile

from core.permissions import NinjaIsMember
from core.api_schemas import ErrorResponse
from core.models import Track

from .api_schemas import MemberProfileResponse, MemberTaskUpdateRequest, RecivedTaskMember, TaskRequest, TaskResponse
from .serializers import MemberProfileMSGSerializer, RecivedTaskMSGSerializer
from .models import Member, ReciviedTask, ReciviedTaskFile

from organizer.models import Attendance, AttendanceStatus

from technical.serializers import TaskMSGSerializer
from technical.models import Task
from technical.caches import (
    members_by_technicals_cache_key, 
    tasks_from_memebrs_cache_key, 
    technical_tasks_cache_key,
    task_view_cache_key, 
)

from utils import DEFAULT_CACHE_DURATION, JSON_CONTENT_TYPE, SAFE_MIMETYPES, serializer_encoder
from .caches import member_profile_cache_key, tasks_cache_key
from channels.layers import get_channel_layer
import mimetypes
import logging
import os

logger = logging.getLogger("member")

@api_controller('/member/tasks/', tags=['Member'], permissions=[NinjaIsMember])
class TasksController:
    
    @route.get("", response={200: list[TaskResponse]})
    async def get_all(self, request: HttpRequest):
        TRACK: Track = request.user.track # type: ignore
        CACHE_KEY = tasks_cache_key(TRACK.name, request.user.id) # type: ignore
        
        if (data:= await cache.aget(CACHE_KEY)):
            return HttpResponse(data, content_type=JSON_CONTENT_TYPE)
        
        tasks = (
            Task.objects
            .filter(track=TRACK)
            .annotate(
                expired=ExpressionWrapper(
                    Q(expires_at__lte=timezone.now()),
                    output_field=BooleanField()
                )
            )
            .exclude(
                id__in=Subquery(
                    ReciviedTask.objects
                    .only("id", "task_id")
                    .filter(member__code=request.user.member.code) # type: ignore
                    .values("task_id")
                )
            )
            .values('id', 'task_number', 'created_at', 'expires_at', 'description', 'expired')
        )
        
        encoded_data = serializer_encoder.encode(await TaskMSGSerializer.afrom_queryset_values(tasks))
        await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)
    
    @route.post("", response={201: None, 400: ErrorResponse})
    async def submit_task(self, request: HttpRequest, payload: Form[TaskRequest], files: File[list[UploadedFile]] = []):
        member: Member = request.user.member # type: ignore
        TRACK: Track = request.user.track # type: ignore
        
        task = await aget_object_or_404(Task.objects.only("id", "task_number", "created_at", "expires_at"), id=payload.task_id)
        
        @sync_to_async
        def safe_transaction():
            with transaction.atomic():
                try:
                    rec_task = ReciviedTask.objects.create(
                        task=task, # type: ignore
                        member=member,
                        track=TRACK,
                        notes=payload.notes
                    )
                    oc_files = (ReciviedTaskFile(recivied_task=rec_task, file=file, file_name=os.path.basename(file.name)) for file in files)
                    ReciviedTaskFile.objects.bulk_create(oc_files)
                    
                    return status.HTTP_201_CREATED, {}
                except IntegrityError as e:
                    return status.HTTP_400_BAD_REQUEST, {"details": "this task already exists"}
                
                except Exception as e:
                    return status.HTTP_400_BAD_REQUEST, {"details": "somthing went wrong, please try again"}
        
        status_code, details = await safe_transaction()
        
        if status_code != 201:
            return status_code, details
             
        await cache.adelete_many(
            [
                tasks_cache_key(TRACK.name, request.user.id), # type: ignore
                task_view_cache_key(payload.task_id),
                member_profile_cache_key(member.code),
                technical_tasks_cache_key(TRACK.name),
                members_by_technicals_cache_key(TRACK.name),
            ]
        )
        cache.delete_pattern(f"technical_recived_tasks_{TRACK.name}*") # type: ignore
        
        channel_layer = get_channel_layer()
        group_name = f"technical_{TRACK.name.replace(' ', '_')}_notifications"
        
        await channel_layer.group_send( # type: ignore
            group_name,
            {
                "type": "broadcast_technical",
                "data": {
                    "message": _("Member {username} sent task {task_number}").format(
                        username= request.user.username,
                        task_number= task.task_number
                    )
                }
            }
        )
        return status_code, details

@api_controller("/member/protected_media/tasks", tags=["Member"], permissions=[IsAuthenticated])
class ProtectedTaskController:

    @route.get("/{sent_task_id}/", response={200: None, 404: None})
    async def get_protected_file(self, request: HttpRequest, sent_task_id: int):
        
        document = await aget_object_or_404(ReciviedTaskFile.objects.only("id", 'file', "file_name", "recivied_task__member__bdaya_user__email").select_related('recivied_task__member__bdaya_user'), id=sent_task_id)
        
        # check if it's an organizer or technical to get the file or check if the user is a member and it's the same member that uplouded this task
        if (request.user.is_member and document.recivied_task.member.bdaya_user.email != request.user.email): # type: ignore
            return status.HTTP_404_NOT_FOUND, {}
        
        content_type, _ = mimetypes.guess_type(document.file.url)
        
        nginx_url = f"/api/media/{document.file.name}"
        final_content_type = content_type or 'application/octet-stream'

        disposition_type = 'inline' if final_content_type in SAFE_MIMETYPES else 'attachment'
        
        response = HttpResponse(b"", content_type=final_content_type)
        response['X-Accel-Redirect'] = nginx_url
        response['Content-Disposition'] = f'{disposition_type}; filename="{document.file_name}"'

        return response

@api_controller("/member/profile", tags=["Member"], permissions=[IsAuthenticated])
class MemberProfileController:
    
    @staticmethod
    def get_sub_queries():
        absents_subquery = Subquery(
            Attendance.objects.filter(
                member=OuterRef('pk'),
                status__in=(AttendanceStatus.ABSENT, AttendanceStatus.EXCUSED)
            )
            .values('member')
            .annotate(cnt=Count('id'))
            .values('cnt')
        )

        tasks_sent_subquery = Subquery(
            ReciviedTask.objects.filter(
                member=OuterRef('pk')
            )
            .values('member')
            .annotate(cnt=Count('id'))
            .values('cnt')
        )
        
        tasks_prefetch = Prefetch(
            'tasks_sent',
            queryset=ReciviedTask.objects.select_related(
                'task',
                'track',
            ).prefetch_related(
                'files'
            ),
            to_attr='tasks_prefetched' 
        )

        return Member.objects.select_related("track", 'bdaya_user').prefetch_related(tasks_prefetch).annotate(
            absents=Coalesce(absents_subquery, 0),
            total_tasks_sent=Coalesce(tasks_sent_subquery, 0),
            total_tasks=Count("track__tasks")
        ).annotate(
            missing_tasks=ExpressionWrapper(
                F("total_tasks") - F("total_tasks_sent"),
                output_field=PositiveSmallIntegerField()
            ),
        )
    
    @route.get("/{member_code}/", response={200: MemberProfileResponse})
    async def get_profile(self, request: HttpRequest, member_code: str):
        if request.user.is_member: # type: ignore
            target_code = request.user.member.code # type: ignore
        else:
            target_code = member_code
        
        if (cached_data := await cache.aget(member_profile_cache_key(target_code))):
            return HttpResponse(cached_data, content_type=JSON_CONTENT_TYPE)
        
        query = self.get_sub_queries()
        member = await aget_object_or_404(
            query,
            code=target_code
        )
        
        data = MemberProfileMSGSerializer.from_model(member)
        encoded_data = data.encode()
        await cache.aset(member_profile_cache_key(data.code), encoded_data, 1800) # 30 minutes
        
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

@api_controller("/member/edit-task", tags=['Member'], permissions=[NinjaIsMember])
class MemberEditTaskController:
    
    @route.get("/{sent_task_id}/", response={200: RecivedTaskMember})
    async def get_editable_task(self, request: HttpRequest, sent_task_id: int):
        task = await aget_object_or_404(
            ReciviedTask.objects
            .select_related("task", "member__bdaya_user", "track")
            .prefetch_related("files")
            .defer(
                "task__track",
                "member__collage_code",
                "member__bonus",
                "member__track",
                "member__joined_at",
                "member__status",
            ), 
            id=sent_task_id, 
            member__code=request.user.member.code # type: ignore
        )
        task_serialized_encoded = RecivedTaskMSGSerializer.from_model(task).encode()
        return HttpResponse(task_serialized_encoded, content_type=JSON_CONTENT_TYPE)
    
    @route.put("/{sent_task_id}/", response={204: None, 404: ErrorResponse})
    async def update_my_task(self, request: HttpRequest, sent_task_id: int, payload: Form[MemberTaskUpdateRequest], files: File[list[UploadedFile]] = []):
        task = await aget_object_or_404(ReciviedTask.objects.only("notes", "signed", "member__code", "task_id").select_related("member", "task"), id=sent_task_id, member__bdaya_user__email=request.user.email) # type: ignore
        update_fields: set[str] = {"signed"}
        
        @sync_to_async
        def safe_transaction() -> None:
            needs_save: bool = False
            with transaction.atomic():
                if payload.notes is not None:
                    task.notes = payload.notes
                    update_fields.add("notes")
                    needs_save = True
                
                if files:
                    ReciviedTaskFile.objects.filter(recivied_task=task).delete()
                    task_files = (
                        ReciviedTaskFile(recivied_task=task, file=file)
                        for file in files
                    )
                    ReciviedTaskFile.objects.bulk_create(task_files)
                    needs_save = True
                
                if needs_save:
                    task.signed = False
                    task.save(update_fields=update_fields)
                    
        await safe_transaction()
        await cache.adelete_many(
            [
                member_profile_cache_key(task.member.code),
                tasks_from_memebrs_cache_key(request.user.track, task.task.pk) # type: ignore
            ]
        )
        
        return status.HTTP_204_NO_CONTENT, {}
