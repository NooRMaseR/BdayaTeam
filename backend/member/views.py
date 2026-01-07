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
# from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models.functions import Coalesce
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
from member.auth import CookieTokenAuthentication
from organizer.models import Attendance, AttendanceStatus

from technical.serializers import TaskSerializer
from technical.models import Task
from . import serializers, models
import mimetypes, os

# Create your views here.
class Tasks(APIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = TaskSerializer
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsMember())
        return perms
    
    def get(self, request: Request) -> Response:
        CACHE_KEY = f"member_tasks_{request.user.email}"
        if (data:=cache.get(CACHE_KEY)):
            return Response(data)
        
        tasks = (
            Task.objects
            .select_related("track")
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
        )
        data = TaskSerializer(tasks, many=True).data
        cache.set(CACHE_KEY, data, 300)
        return Response(data)
    
    @extend_schema(
        request=inline_serializer(
            "task-member-input",
            {
                "task_id": serializers.serializers.IntegerField(),
                "file": serializers.serializers.ListField(
                    child=serializers.serializers.FileField(),
                    required=False
                ),
                "notes": serializers.serializers.CharField(required=False)
            }
        ),
        responses={
            201: None,
            400: inline_serializer(
                name="badTask",
                fields={
                    "details": serializers.serializers.CharField(default="error here")
                }
            ),
            406: inline_serializer(
                name="taskExpired",
                fields={
                    "details": serializers.serializers.CharField(default="task is expired")
                }
            )
        }
    )
    def post(self, request: Request) -> Response:
        member = get_object_or_404(models.Member.objects.only("code"), email=request.user.email)
        task = get_object_or_404(models.Task.objects.only("id", "created_at", "expires_at"), id=request.data.get("task_id")) # type: ignore
        
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
            cache.delete(f"member_profile_{member.code}")
            return Response(status=status.HTTP_201_CREATED)
        
        except IntegrityError:
            return Response({"details": "this task already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(repr(e))
            return Response({"details": "somthing went wrong, please try again"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(xframe_options_exempt, name='dispatch')
class ProtectedTask(APIView):
    authentication_classes = (CookieTokenAuthentication,)
    
    def get(self, request: Request, task_id: int) -> HttpResponse:
        document = get_object_or_404(models.ReciviedTaskFile.objects.only("id", 'file', "recivied_task__member__email").select_related('recivied_task__member'), id=task_id)
        
        # check if it's an organizer or technical to get the file or check if the user is a member and it's the same member that uplouded this task
        if (not request.user.role in (UserRole.ORGANIZER, UserRole.TECHNICAL) and document.recivied_task.member.email != request.user.email):
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        content_type, _ = mimetypes.guess_type(document.file.url)
        
        return Response(
            headers={
                "X-Accel-Redirect": document.file.url,
                'Content-Disposition': f'inline; filename="{os.path.basename(document.file.name)}"'
            },
            content_type=content_type or 'application/octet-stream'
        )

class MemberProfile(APIView):
    serializer_class = serializers.MemberProfileSerializer
    
    def get_sub_querys(self):
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
    
    def get(self, request: Request, member_code: str) -> Response:
        CACHE_KEY = f"member_profile_{member_code}"
        if (data:=cache.get(CACHE_KEY)):
            return Response(data)
        
        query = self.get_sub_querys()
        
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
                
        data = serializers.MemberProfileSerializer(user).data
        cache.set(CACHE_KEY, data, 300)
        return Response(data)
        