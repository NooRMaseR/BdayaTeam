from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
)

from core.models import Track
from core.api_schemas import ForbiddenOnlyTechnical
from core.serializers import TrackNameOnlyMSGSerializer
from core.permissions import IsTechnical, IsTechnicalOrMember

from member.auth import RawJsonRenderer
from member.models import Member, ReciviedTask
from member.api_schemas import MemberTechnicalSerializer, RecivedTaskSerializer
from member.serializers import (
    MemberTechnicalMSGSerializer,
    RecivedTaskMSGSerializer,
)

from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
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

from member.views import MemberProfile
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
        if cached := cache.get(self.get_cache_key(TRACK.name)):
            return Response(cached)
        
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
            models.Task.objects
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
        
        encoded_data = serializer_encoder.encode(TaskMSGSerializer.from_queryset_values(data))
        cache.set(self.get_cache_key(TRACK.name), encoded_data, DEFAULT_CACHE_DURATION)
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
            cache.delete(self.get_cache_key(request.user.track.name))
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
            TaskMSGSerializer.from_model_values(data)
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

        if not has_data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            models.Task.objects.filter(id=task_id).update(**data_to_update)
            cache.delete_many(
                [
                    self.get_cache_key(task_id),
                    Tasks.get_cache_key(request.user.track.name)
                ]
            )
            return Response()
        except Exception as e:
            return Response(
                {"details": repr(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def delete(self, request: Request, task_id: int) -> Response:
        get_object_or_404(models.Task, id=task_id).delete()
        cache.delete_many(
            [
                self.get_cache_key(task_id),
                Tasks.get_cache_key(request.user.track.name),
                MemberProfile.get_cache_key(request.user.member.code)
            ]
        )
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
        track: Track = request.user.track
        CACHE_KEY = self.get_cache_key(track.name, task_id)
        if cached := cache.get(CACHE_KEY):
            return Response(cached)

        tasks = (
            ReciviedTask.objects
            .select_related("track", "task", "member")
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
            .filter(
                track=track,
                task_id=task_id,
                signed=False
            )
        )
        
        encoded_data = serializer_encoder.encode(RecivedTaskMSGSerializer.from_queryset(tasks))
        cache.set(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)

    @extend_schema(
        request=inline_serializer(
            name="TaskSigning",
            fields={
                "degree": api_schemas.serializers.IntegerField(),
                "technical_notes": api_schemas.serializers.CharField(required=False),
            },
        ),
        responses={200: None},
    )
    def post(self, request: Request, task_id: int) -> Response:
        track: Track = request.user.track
        recived_task = get_object_or_404(ReciviedTask.objects.select_related('task', 'member'), id=task_id, track=track)
        try:
            ReciviedTask.objects.filter(id=recived_task.pk).update(
                degree=int(request.data.get("degree")), # type: ignore
                technical_notes=request.data.get('technical_notes'), # type: ignore
                signed=True
            )
            
            cache.delete_many(
                [
                    self.get_cache_key(track.name, recived_task.task.pk),
                    MemberProfile.get_cache_key(recived_task.member.code),
                    Tasks.get_cache_key(track.name)
                ]
            )
        except Exception as e:
            return Response({"details": repr(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response()


class Members(APIView):
    permission_classes = (IsTechnical,)
    renderer_classes = (RawJsonRenderer,)
    
    @staticmethod
    def get_cache_key(track_name: str) -> str:
        return f"members_tech_{track_name}"

    @extend_schema(responses={200: MemberTechnicalSerializer(many=True)})
    def get(self, request: Request, track_name: str) -> Response:
        TRACK = track_name.replace("%20", " ")
        track_obj: Track = request.user.track
        
        if request.user.is_technical and track_obj.name != TRACK:
            return Response({"details": f"Not Your Track {request.user.username}"}, status=status.HTTP_403_FORBIDDEN)

        CACHE_KEY = self.get_cache_key(track_name)
        if cached_data := cache.get(CACHE_KEY):
            return Response(cached_data)
        
        track_serialized = TrackNameOnlyMSGSerializer.from_model(track_obj)

        members = (
            Member.objects
            .prefetch_related(
                Prefetch(
                    "tasks_sent",
                    ReciviedTask.objects.select_related('task'),
                    "prefetched_tasks"
                )
            )
            .defer('joined_at')
            .order_by("joined_at")
            .filter(track=track_obj)
        )
        
        data = MemberTechnicalMSGSerializer.from_queryset_with_track(members, track_serialized)
        encoded_data = serializer_encoder.encode(data)
        cache.set(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)
    
    @extend_schema(
        request=inline_serializer(
            "editMemberTask",
            {
                "code": api_schemas.serializers.CharField(),
                "task_id": api_schemas.serializers.IntegerField(),
                "field": api_schemas.serializers.ChoiceField(models.MemberTechEditType),
                "value": api_schemas.serializers.CharField(),
            },
        ),
        examples=[
            OpenApiExample(
                "Update a Field Example",
                {
                    "code": "c-2",
                    "task_id": 1,
                    "field": models.MemberTechEditType.DEGREE,
                    "value": 2,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Create Attendance Example",
                {
                    "code": "p-2",
                    "task_id": 1,
                    "field": models.MemberTechEditType.NOTES,
                    "value": "nice job!!",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request: Request, track_name: str) -> Response:
        code: str | None = request.data.get("code") # type: ignore
        task_id: int | None = request.data.get("task_id") # type: ignore
        value: str | int | None = request.data.get("value") # type: ignore
        
        if not value:
            return Response({"details": "value is required"})
        
        try:
            field = models.MemberTechEditType(request.data.get("field")) # type: ignore
        except ValueError:
            return Response({"details": "field not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        
        recivied_task = get_object_or_404(ReciviedTask.objects.only("id", "notes", "degree"), task_id=task_id, member__code=code)
        
        match field:
            case models.MemberTechEditType.NOTES:
                recivied_task.notes = str(value)
            case models.MemberTechEditType.DEGREE:
                recivied_task.degree = int(value)
                
        recivied_task.save()
        cache.delete(self.get_cache_key(track_name))
        return Response()