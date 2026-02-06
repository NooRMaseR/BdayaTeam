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
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import (
    PositiveSmallIntegerField, 
    ExpressionWrapper, 
    BooleanField, 
    Subquery, 
    OuterRef,
    Count, 
    Q, 
    F, 
)

from core.models import UserRole
from core.permissions import IsMember
from core.serializers import TrackNameOnlyMSGSerializer
from organizer.models import Attendance, AttendanceStatus

from member.serializers import MemberProfileMSGSerializer
from member.auth import RawJsonRenderer

from technical.serializers import TaskMSGSerializer
from technical.api_schemas import TaskSerializer
from technical.models import Task

from utils import SAFE_MIMETYPES, serializer_encoder, DEFAULT_CACHE_DURATION
from . import api_schemas, models
import mimetypes, os

# Create your views here.

class Tasks(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TaskSerializer(many=True)
    renderer_classes = (RawJsonRenderer,)
    permission_classes = (IsMember,)
    
    @staticmethod
    def get_cache_key(member_id: int):
        return f"member_tasks_{member_id}"
    
    def get(self, request: Request) -> Response:
        CACHE_KEY = self.get_cache_key(request.user.id)
        if (data:=cache.get(CACHE_KEY)):
            return Response(data)
        
        tasks = (
            Task.objects
            .filter(track=request.user.track)
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
                    .filter(member__email=request.user.email)
                    .values("task_id")
                )
            )
            .values('id', 'task_number', 'created_at', 'expires_at', 'description', 'expired')
        )
        
        encoded_data = serializer_encoder.encode([
            TaskMSGSerializer(
                id=task['id'],
                task_number=task['task_number'],
                created_at=task['created_at'],
                expires_at=task['expires_at'],
                description=task['description'],
                expired=task['expired'],
            )
            for task in tasks
        ])
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
    def post(self, request: Request) -> Response:
        TASK_ID: int | None = request.data.get("task_id") # type: ignore
        member = get_object_or_404(models.Member.objects.only("code"), email=request.user.email)
        task = get_object_or_404(models.Task.objects.only("id", "created_at", "expires_at"), id=TASK_ID) # type: ignore
        
        if task.is_expired:
            return Response({"details": "task is expired"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        try:
            with transaction.atomic():
                rec_task = models.ReciviedTask.objects.create(
                    task=task, # type: ignore
                    member=member,
                    track=request.user.track,
                    notes=request.data.get("notes") # type: ignore
                )
                oc_files = (models.ReciviedTaskFile(recivied_task=rec_task, file=f) for f in request.data.getlist("file")) # type: ignore
                models.ReciviedTaskFile.objects.bulk_create(oc_files)
            cache.delete(self.get_cache_key(request.user.id))
            cache.delete(f"task_view:i{TASK_ID}")
            cache.delete(MemberProfile.get_cache_key(member.code))
            cache.delete_pattern(f"technical_recived_tasks_{request.user.track}*") # type: ignore
            return Response({}, status=status.HTTP_201_CREATED)
        
        except IntegrityError:
            return Response({"details": "this task already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(repr(e))
            return Response({"details": "somthing went wrong, please try again"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(xframe_options_exempt, name='dispatch')
class ProtectedTask(APIView):
    serializer_class = None
    
    def get(self, request: Request, task_id: int) -> HttpResponse:
        document = get_object_or_404(models.ReciviedTaskFile.objects.only("id", 'file', "recivied_task__member__email").select_related('recivied_task__member'), id=task_id)
        
        # check if it's an organizer or technical to get the file or check if the user is a member and it's the same member that uplouded this task
        if (request.user.role == UserRole.MEMBER and document.recivied_task.member.email != request.user.email):
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        content_type, _ = mimetypes.guess_type(document.file.url)
        
        nginx_url = f"/api/media/{document.file.name}"
        final_content_type = content_type or 'application/octet-stream'

        disposition_type = 'inline' if final_content_type in SAFE_MIMETYPES else 'attachment'
        
        return Response(
            headers={
                "X-Accel-Redirect": nginx_url,
                'Content-Disposition': f'{disposition_type}; filename="{os.path.basename(document.file.name)}"'
            },
            content_type=content_type or 'application/octet-stream'
        )

class MemberProfile(APIView):
    serializer_class = api_schemas.MemberProfileSerializer
    renderer_classes = (RawJsonRenderer,)
    
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

        return models.Member.objects.select_related("track").annotate(
            absents=Coalesce(absents_subquery, 0),
            total_tasks_sent=Coalesce(tasks_sent_subquery, 0),
            total_tasks=Count("track__tasks")
        ).annotate(
            missing_tasks=ExpressionWrapper(
                F("total_tasks") - F("total_tasks_sent"),
                output_field=PositiveSmallIntegerField()
            )
        )
    
    @staticmethod
    def get_cache_key(code: str):
        return f"member_profile_{code}"
    
    def get(self, request: Request, member_code: str) -> Response:
        if (data:=cache.get(self.get_cache_key(member_code))):
            return Response(data)
        
        query = self.get_sub_queries()
        
        match request.user.role:
            case UserRole.MEMBER:
                user = get_object_or_404(
                    query,
                    email=request.user.email
                )
            case _:
                user = get_object_or_404(
                    query,
                    code=member_code
                )
        
        data = MemberProfileMSGSerializer(
            absents=user.absents, # type: ignore
            track=TrackNameOnlyMSGSerializer(
                user.track.pk,
                user.track.track,
            ),
            total_tasks_sent=user.total_tasks_sent, # type: ignore
            missing_tasks=user.missing_tasks, # type: ignore
            name=user.name,
            code=user.code,
        )
        encoded_data = serializer_encoder.encode(data)
        cache.set(self.get_cache_key(data.code), encoded_data, 1800) # 30 minutes
        return Response(encoded_data)

