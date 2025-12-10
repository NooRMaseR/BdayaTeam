from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from core.serializers import ForbiddenOnlyTechnical
from core.permissions import IsTechnical
from . import models, serializers

from member.models import ReciviedTask
from member.serializers import RecivedTaskSerializer

from django.utils import timezone
from django.db.models import Q, ExpressionWrapper, BooleanField

# Create your views here.


class Tasks(APIView):
    
    def get_permissions(self):
        perm = super().get_permissions()
        perm.append(IsTechnical())
        return perm
    
    @extend_schema(
        description="Get the Tasks that are related to the technical track",
        responses={
            200: serializers.TaskSerializer(many=True),
            403: ForbiddenOnlyTechnical()
        },
    )
    def get(self, request: Request) -> Response:
        data = (
            models.Task.objects
            .select_related("track")
            .defer("track__prefix")
            .filter(track=request.user.track)
            .annotate(
                expired=ExpressionWrapper(
                    Q(expires_at__lte=timezone.now()),
                    output_field=BooleanField()
                )
            )
        )
        return Response(serializers.TaskSerializer(data, many=True).data)
    
    @extend_schema(
        request=serializers.TaskSerializer(),
        responses={
            200: serializers.TaskSerializer(),
            400: inline_serializer(
                "bad-task",
                {
                    "field": serializers.serializers.ListField(default=["field error message"])
                }
            ),
            403: ForbiddenOnlyTechnical()
        }
    )
    def post(self, request: Request) -> Response:
        serializer = serializers.TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class TasksFromMembers(APIView):
    serializer_class = RecivedTaskSerializer(many=True)
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsTechnical())
        return perms
    
    def get(self, request: Request) -> Response:
        tasks = ReciviedTask.objects.select_related("track", "task", "member").prefetch_related("files").filter(track=request.user.track)
        serializer = RecivedTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=inline_serializer(
            name="TaskSigning",
            fields={
                "task_id": serializers.serializers.IntegerField(),
                "degree": serializers.serializers.IntegerField()
            }
        ),
        responses={
            200: None
        }
    )
    def post(self, request: Request) -> Response:
        ReciviedTask.objects.filter(id=request.data.get("task_id"), track=request.user.track).update(degree=request.data.get("degree"), signed=True) # type: ignore
        return Response()