from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, inline_serializer

from django.db import transaction
from django.utils import timezone
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Subquery, BooleanField, ExpressionWrapper, Q

from core.permissions import IsMember

from . import serializers, models
from technical.models import Task
from technical.serializers import TaskSerializer


# Create your views here.
class Tasks(APIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = TaskSerializer
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsMember())
        return perms
    
    def get(self, request: Request) -> Response:
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
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
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
        member = get_object_or_404(models.Member, email=request.user.email)
        task = get_object_or_404(models.Task, id=request.data.get("task_id")) # type: ignore
        
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
            return Response(status=status.HTTP_201_CREATED)
        
        except IntegrityError:
            return Response({"details": "this task already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(repr(e))
            return Response({"details": "somthing went wrong, please try again"}, status=status.HTTP_400_BAD_REQUEST)
        