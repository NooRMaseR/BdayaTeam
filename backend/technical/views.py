from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from core.models import Track
from core.api_schemas import ForbiddenOnlyTechnical
from core.serializers import TrackNameOnlyMSGSerializer
from core.permissions import IsTechnical, IsTechnicalOrMember

from member.auth import RawJsonRenderer
from member.models import ReciviedTask
from member.api_schemas import RecivedTaskSerializer
from member.serializers import MemberMSGSerializerForTask, RecivedFile, RecivedTaskMSGSerializer

from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db.models import Q, ExpressionWrapper, BooleanField

from utils import DEFAULT_CACHE_DURATION, serializer_encoder
from technical.serializers import TaskMSGSerializer
from . import api_schemas, models

# Create your views here.


class Tasks(APIView):
    permission_classes = (IsTechnical,)

    def get_renderers(self):
        if self.request.method == "GET":
            return [RawJsonRenderer()]
        return super().get_renderers()

    @staticmethod
    def get_cache_key(track_name: str):
        return f"technical_tasks:t{track_name}"

    @extend_schema(
        description="Get the Tasks that are related to the technical track",
        responses={
            200: api_schemas.TaskSerializer(many=True),
            403: ForbiddenOnlyTechnical(),
        },
    )
    def get(self, request: Request) -> Response:
        TRACK: Track = request.user.track
        if cached := cache.get(self.get_cache_key(TRACK.track)):
            return Response(cached)

        data = (
            models.Task.objects.filter(track=TRACK)
            .annotate(
                expired=ExpressionWrapper(
                    Q(expires_at__lte=timezone.now()), output_field=BooleanField()
                )
            )
            .values("id", "task_number", "created_at", "expires_at", "description", "expired")
        )
        
        encoded_data = serializer_encoder.encode(
            [
                TaskMSGSerializer(
                    id=t["id"],
                    task_number=t["task_number"],
                    created_at=t["created_at"],
                    expires_at=t["expires_at"],
                    expired=t["expired"],
                    description=t["description"],
                )
                for t in data
            ]
        )
        cache.set(self.get_cache_key(TRACK.track), encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)

    @extend_schema(
        request=api_schemas.TaskSerializer(),
        responses={
            200: api_schemas.TaskSerializer(),
            400: inline_serializer(
                "bad-task",
                {
                    "field": api_schemas.serializers.ListField(
                        default=["field error message"]
                    )
                },
            ),
            403: ForbiddenOnlyTechnical(),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = api_schemas.TaskSerializer(data=request.data, context={'track': request.user.track})
        if serializer.is_valid():
            serializer.save(track=request.user.track)
            cache.delete(self.get_cache_key(request.user.track.track))
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskView(APIView):

    def get_renderers(self):
        if self.request.method == "GET":
            return [RawJsonRenderer()]
        return super().get_renderers()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsTechnicalOrMember()]
        return [IsTechnical()]

    @staticmethod
    def get_cache_key(task_id: int) -> str:
        return f"task_view:i{task_id}"

    @extend_schema(
        description="Get the Tasks that are related to the technical track",
        responses={
            200: api_schemas.TaskSerializer(),
        },
    )
    def get(self, request: Request, task_id: int) -> Response:
        if cached := cache.get(self.get_cache_key(task_id)):
            return Response(cached)

        data = get_object_or_404(
            models.Task.objects.annotate(
                expired=ExpressionWrapper(
                    Q(expires_at__lte=timezone.now()), output_field=BooleanField()
                )
            )
            .values("id", "task_number", "description", "created_at", "expires_at", "expired"), # type: ignore
            id=task_id,
        )
        
        encoded_data = serializer_encoder.encode(
            TaskMSGSerializer(
                id=data["id"],
                task_number=data["task_number"],
                created_at=data["created_at"],
                expires_at=data["expires_at"],
                expired=data["expired"],
                description=data["description"],
            )
        )
        cache.set(self.get_cache_key(task_id), encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)

    @extend_schema(
        request=inline_serializer(
            "updateTask",
            {
                "task_number": api_schemas.serializers.IntegerField(),
                "expires_at": api_schemas.serializers.DateTimeField(),
                "description": api_schemas.serializers.CharField(),
            },
        )
    )
    def put(self, request: Request, task_id: int) -> Response:

        data_to_update: dict[str, str] = {}
        has_data: bool = False

        if ex := request.data.get("task_number"):  # type: ignore
            data_to_update["task_number"] = ex
            has_data = True

        if ex := request.data.get("expires_at"):  # type: ignore
            data_to_update["expires_at"] = ex
            has_data = True

        if ex := request.data.get("description"):  # type: ignore
            data_to_update["description"] = ex
            has_data = True

        if has_data:
            try:
                models.Task.objects.filter(id=task_id).update(**data_to_update)
                cache.delete(self.get_cache_key(task_id))
                cache.delete(Tasks.get_cache_key(request.user.track.track))
            except Exception as e:
                return Response(
                    {"details": repr(e)}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request: Request, task_id: int) -> Response:
        get_object_or_404(models.Task, id=task_id).delete()
        cache.delete(self.get_cache_key(task_id))
        cache.delete(Tasks.get_cache_key(request.user.track.track))
        return Response(status=status.HTTP_204_NO_CONTENT)


class TasksFromMembers(APIView):
    serializer_class = RecivedTaskSerializer(many=True)
    permission_classes = (IsTechnical,)
    
    def get_renderers(self):
        if self.request.method == "GET":
            return [RawJsonRenderer()]
        return super().get_renderers()

    @staticmethod
    def get_cache_key(track_name: str, task_id: int) -> str:
        return f"technical_recived_tasks_{track_name}:i{task_id}"

    def get(self, request: Request, task_id: int) -> Response:
        CACHE_KEY = self.get_cache_key(request.user.track.track, task_id)
        if cached := cache.get(CACHE_KEY):
            return Response(cached)

        tasks = (
            ReciviedTask.objects.select_related("track", "task", "member")
            .prefetch_related("files")
            .defer(
                "task__track",
                "member__email",
                "member__collage_code",
                "member__phone_number",
                "member__bonus",
                "member__track",
                "member__joined_at",
                "member__status",
            )
            .filter(track=request.user.track, task_id=task_id)
        )
        
        encoded_data = serializer_encoder.encode([
            RecivedTaskMSGSerializer(
                task=TaskMSGSerializer(
                    id=t.task.pk,
                    task_number=t.task.task_number,
                    created_at=t.task.created_at,
                    expires_at=t.task.expires_at,
                    description=t.task.description,
                    expired=t.task.is_expired
                ),
                member=MemberMSGSerializerForTask(
                    t.member.code,
                    t.member.name,
                ),
                track=TrackNameOnlyMSGSerializer(
                    t.track.pk,
                    t.track.track,
                ),
                id=t.pk,
                notes=t.notes,
                degree=t.degree,
                signed=t.signed,
                recived_at=t.recived_at,
                files_url=[RecivedFile(id=f.id, file_url=f.file.url) for f in t.files.all() if f.file] # type: ignore
            )
            for t in tasks
        ])
        cache.set(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)

    @extend_schema(
        request=inline_serializer(
            name="TaskSigning",
            fields={
                "task_id": api_schemas.serializers.IntegerField(),
                "degree": api_schemas.serializers.IntegerField(),
            },
        ),
        responses={200: None},
    )
    def post(self, request: Request, task_id: int) -> Response:
        ReciviedTask.objects.select_for_update().filter(id=request.data.get("task_id"), track=request.user.track).update(degree=request.data.get("degree"), signed=True)  # type: ignore
        cache.delete(self.get_cache_key(request.user.track.track, task_id))
        return Response()
