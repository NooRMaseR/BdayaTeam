from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, inline_serializer

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.http import HttpResponse
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.core.files.uploadedfile import UploadedFile
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

from core.models import Track
from core.permissions import IsMember
from organizer.models import Attendance, AttendanceStatus

from . import api_schemas, models
from .caches import member_profile_cache_key, tasks_cache_key
from .serializers import MemberProfileMSGSerializer, RecivedTaskMSGSerializer

from technical.models import Task
from technical.api_schemas import TaskSerializer
from technical.serializers import TaskMSGSerializer
from technical.caches import (
    members_by_technicals_cache_key,
    tasks_from_memebrs_cache_key,
    technical_tasks_cache_key,
    task_view_cache_key,
)


from utils import SAFE_MIMETYPES, serializer_encoder, DEFAULT_CACHE_DURATION
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import mimetypes, logging

# Create your views here.

logger = logging.getLogger("member")

class BaseMemberAPIView(APIView):
    permission_classes = (IsMember,)

class Tasks(BaseMemberAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TaskSerializer(many=True)
    
    def get(self, request: Request) -> Response:
        TRACK: Track = request.user.track
        CACHE_KEY = tasks_cache_key(TRACK.name, request.user.id)
        if (data:=cache.get(CACHE_KEY)):
            return Response(data)
        
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
                    models.ReciviedTask.objects
                    .only("id", "task_id")
                    .filter(member__code=request.auth.get("code"))
                    .values("task_id")
                )
            )
            .values('id', 'task_number', 'created_at', 'expires_at', 'description', 'expired')
        )
        
        encoded_data = serializer_encoder.encode(TaskMSGSerializer.from_queryset_values(tasks))
        cache.set(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)
    
    @extend_schema(
        request=inline_serializer(
            "task-member-input",
            {
                "task_id": api_schemas.serializers.IntegerField(),
                "file": api_schemas.serializers.ListField(
                    child=api_schemas.serializers.FileField(),
                    required=False
                ),
                "notes": api_schemas.serializers.CharField(required=False)
            }
        ),
        responses={
            201: None,
            400: inline_serializer(
                name="badTask",
                fields={
                    "details": api_schemas.serializers.CharField(default="error here")
                }
            ),
            406: inline_serializer(
                name="taskExpired",
                fields={
                    "details": api_schemas.serializers.CharField(default="task is expired")
                }
            )
        }
    )
    @transaction.atomic
    def post(self, request: Request) -> Response:
        TASK_ID: int | None = request.data.get("task_id") # type: ignore
        member: models.Member = request.user.member
        TRACK: Track = request.user.track
        
        if TASK_ID is None:
            return Response({"details": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        task = get_object_or_404(models.Task.objects.only("id", "task_number", "created_at", "expires_at"), id=TASK_ID)
        
        try:
            rec_task = models.ReciviedTask.objects.create(
                task=task, # type: ignore
                member=member,
                track=TRACK,
                notes=request.data.get("notes") # type: ignore
            )
            oc_files = (models.ReciviedTaskFile(recivied_task=rec_task, file=f) for f in request.data.getlist("file")) # type: ignore
            models.ReciviedTaskFile.objects.bulk_create(oc_files)
            
            cache.delete_many(
                [
                    tasks_cache_key(TRACK.name, request.user.id),
                    task_view_cache_key(TASK_ID),
                    member_profile_cache_key(member.code),
                    technical_tasks_cache_key(TRACK.name),
                    members_by_technicals_cache_key(TRACK.name),
                ]
            )
            cache.delete_pattern(f"technical_recived_tasks_{TRACK.name}*") # type: ignore
            
            channel_layer = get_channel_layer()
            group_name = f"technical_{TRACK.name.replace(' ', '_')}_notifications"
            
            async_to_sync(channel_layer.group_send)( # type: ignore
                group_name,
                {
                    "type": "broadcast_technical",
                    "data": {
                        "message": f"Member {request.user.username} sent task {task.task_number}"
                    }
                }
            )
            return Response({}, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            logger.warning(repr(e))
            return Response({"details": "this task already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(repr(e))
            return Response({"details": "somthing went wrong, please try again"}, status=status.HTTP_400_BAD_REQUEST)


# @method_decorator(xframe_options_exempt, name='dispatch')
class ProtectedTask(APIView):
    serializer_class = None
    
    def get(self, request: Request, task_id: int) -> HttpResponse:
        document = get_object_or_404(models.ReciviedTaskFile.objects.only("id", 'file', "file_name", "recivied_task__member__bdaya_user__email").select_related('recivied_task__member__bdaya_user'), id=task_id)
        
        # check if it's an organizer or technical to get the file or check if the user is a member and it's the same member that uplouded this task
        if (request.user.is_member and document.recivied_task.member.bdaya_user.email != request.user.email):
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        content_type, _ = mimetypes.guess_type(document.file.url)
        
        nginx_url = f"/api/media/{document.file.name}"
        final_content_type = content_type or 'application/octet-stream'

        disposition_type = 'inline' if final_content_type in SAFE_MIMETYPES else 'attachment'
        
        return Response(
            headers={
                "X-Accel-Redirect": nginx_url,
                'Content-Disposition': f'{disposition_type}; filename="{document.file_name}"'
            },
            content_type=final_content_type
        )

class MemberProfile(APIView):
    serializer_class = api_schemas.MemberProfileSerializer
    
    def get_sub_queries(self):
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
            models.ReciviedTask.objects.filter(
                member=OuterRef('pk')
            )
            .values('member')
            .annotate(cnt=Count('id'))
            .values('cnt')
        )
        
        tasks_prefetch = Prefetch(
            'tasks_sent',
            queryset=models.ReciviedTask.objects.select_related(
                'task',
                'track',
            ).prefetch_related(
                'files'
            ),
            to_attr='tasks_prefetched' 
        )

        return models.Member.objects.select_related("track", 'bdaya_user').prefetch_related(tasks_prefetch).annotate(
            absents=Coalesce(absents_subquery, 0),
            total_tasks_sent=Coalesce(tasks_sent_subquery, 0),
            total_tasks=Count("track__tasks")
        ).annotate(
            missing_tasks=ExpressionWrapper(
                F("total_tasks") - F("total_tasks_sent"),
                output_field=PositiveSmallIntegerField()
            ),
        )
    
    def get(self, request: Request, member_code: str) -> Response:

        if request.user.is_member:
            target_code = request.auth.get("code") 
        else:
            target_code = member_code
        
        if (cached_data := cache.get(member_profile_cache_key(target_code))):
            return Response(cached_data)
        
        query = self.get_sub_queries()
        member = get_object_or_404(
            query,
            code=target_code
        )
        
        data = MemberProfileMSGSerializer.from_model(member)
        encoded_data = data.encode()
        cache.set(member_profile_cache_key(data.code), encoded_data, 1800) # 30 minutes
        return Response(encoded_data)


class EditMemberSentTask(BaseMemberAPIView):
    serializer_class = api_schemas.RecivedTaskSerializer()
    parser_classes = (MultiPartParser, FormParser)
    
    def get(self, request: Request, sent_task_id: int) -> Response:
        task = get_object_or_404(
            models.ReciviedTask.objects
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
            member__code=request.auth.get("code")
        )
        task_serialized_encoded = RecivedTaskMSGSerializer.from_model(task).encode()
        return Response(task_serialized_encoded)
    
    @extend_schema(
        request=inline_serializer(
            "editMemberSelfTask",
            {
                "files": api_schemas.serializers.ListField(
                    child=api_schemas.serializers.FileField(),
                    required=False
                ),
                "notes": api_schemas.serializers.CharField(required=False)
            }
        ),
        responses={
            200: None
        }
    )
    @transaction.atomic
    def put(self, request: Request, sent_task_id: int) -> Response:
        
        task = get_object_or_404(models.ReciviedTask.objects.only("notes", "signed", "member_code", "task_id").select_related("member", "task"), id=sent_task_id, member__email=request.user.email)
        notes: str | None = request.data.get("notes") # type: ignore
        files: list[UploadedFile] | None = request.FILES.getlist("files") # type: ignore
        needs_save: bool = False
        update_fields: set[str] = {"signed"}
        
        if notes is not None:
            task.notes = notes
            update_fields.add("notes")
            needs_save = True
        
        if files:
            models.ReciviedTaskFile.objects.filter(recivied_task=task).delete()
            task_files = (
                models.ReciviedTaskFile(recivied_task=task, file=file)
                for file in files
            )
            models.ReciviedTaskFile.objects.bulk_create(task_files)
            needs_save = True
        
        if needs_save:
            task.signed = False
            task.save(update_fields=update_fields)
            cache.delete_many(
                [
                    member_profile_cache_key(task.member.code),
                    tasks_from_memebrs_cache_key(request.user.track, task.task.pk)
                ]
            )
        
        return Response()
        
