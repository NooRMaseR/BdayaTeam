from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError, transaction
from django.shortcuts import aget_object_or_404
from django.db.models.functions import Coalesce
from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
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


from core.permissions import get_member_user, get_any_authenticated_user
from core.models import BdayaUser, Track

from .serializers import MemberProfileMSGSerializer, RecivedTaskMSGSerializer
from notifications.tasks import send_notification_to_track_technicals
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

from utils import (
    DEFAULT_CACHE_DURATION,
    serializer_encoder,
    JSON_CONTENT_TYPE,
    SAFE_MIMETYPES,
    FormStr,
    IntId,
)
from .caches import member_profile_cache_key, tasks_cache_key
from channels.layers import get_channel_layer
import mimetypes, asyncio, logging, os
from urllib.parse import quote
from typing import Annotated

from django_bolt import BoltAPI, Depends, Response, UploadFile, status
from django_bolt.exceptions import NotFound, BadRequest
from django_bolt.param_functions import Form, File

logger = logging.getLogger("member")

bolt = BoltAPI(
    prefix="/api/member/",
    trailing_slash="append",
    validate_response=False,
    django_middleware=settings.BOLT_MIDDLEWARE
)


@bolt.get("/tasks/", response_model=list[TaskMSGSerializer])
async def get_all_tasks(user: BdayaUser = Depends(get_member_user)):  # type: ignore
    """get all unsigned tasks
    
    fetches all the tasks that hasen't reviewed yet by a technical `signed=False`
    """
    
    TRACK: Track = user.track  # type: ignore
    CACHE_KEY = tasks_cache_key(TRACK.name, user.id)  # type: ignore

    if data := await cache.aget(CACHE_KEY):
        return HttpResponse(data, content_type=JSON_CONTENT_TYPE)

    tasks = (
        Task.objects.filter(track=TRACK)
        .annotate(
            expired=ExpressionWrapper(
                Q(expires_at__lte=timezone.now()), output_field=BooleanField()
            )
        )
        .exclude(
            id__in=Subquery(
                ReciviedTask.objects.only("id", "task_id")
                .filter(member__code=user.member.code)  # type: ignore
                .values("task_id")
            )
        )
        .values(
            "id", "task_number", "created_at", "expires_at", "description", "expired"
        )
    )

    encoded_data = serializer_encoder.encode(
        await TaskMSGSerializer.afrom_queryset_values(tasks)
    )
    await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)


@bolt.post("/tasks/", status_code=201)
async def submit_task(task_id: Annotated[IntId, Form()], notes: Annotated[str | None, Form()] = None, files: Annotated[list[UploadFile], File(alias="files")] = [], user: BdayaUser = Depends(get_member_user)):  # type: ignore
    "submit task solution"
    
    member: Member = user.member  # type: ignore
    TRACK: Track = user.track  # type: ignore

    try:
        task = await aget_object_or_404(
            Task.objects.only("id", "task_number", "created_at", "expires_at"),
            id=task_id,
        )
    except Task.DoesNotExist:
        raise NotFound(detail=f"Task with id={task_id} does not exists")

    @sync_to_async
    def safe_transaction():
        with transaction.atomic():
            try:
                rec_task = ReciviedTask.objects.create(
                    task=task, member=member, track=TRACK, notes=notes  # type: ignore
                )
                oc_files = (
                    ReciviedTaskFile(
                        recivied_task=rec_task,
                        file=file.file,
                        file_name=os.path.basename(file.filename),
                    )
                    for file in files
                )
                ReciviedTaskFile.objects.bulk_create(oc_files)

                return Response(status_code=status.HTTP_201_CREATED)
            except IntegrityError:
                raise BadRequest(detail="this task already exists")

            except Exception:
                raise BadRequest(detail="somthing went wrong, please try again")

    response = await safe_transaction()

    await cache.adelete_many(
        [
            tasks_cache_key(TRACK.name, user.id),  # type: ignore
            task_view_cache_key(task_id),
            member_profile_cache_key(member.code),
            technical_tasks_cache_key(TRACK.name),
            members_by_technicals_cache_key(TRACK.name),
        ]
    )
    cache.delete_pattern(f"technical_recived_tasks_{TRACK.name}*")  # type: ignore

    channel_layer = get_channel_layer()
    group_name = f"technical_{TRACK.name.replace(' ', '_')}_notifications"

    await asyncio.gather(
        channel_layer.group_send(  # type: ignore
            group_name,
            {
                "type": "broadcast_technical",
                "data": {
                    "message": _("Member {username} sent task {task_number}").format(
                        username=user.username, task_number=task.task_number
                    )
                },
            },
        ),
        send_notification_to_track_technicals(
            track_id=TRACK.pk,
            title=f"{user.username} - {member.code}",
            body=f"Sent Task {task.task_number}",
            url=f"/technical/{TRACK.name}/tasks/{task.pk}",
        ),
    )
    return response


def get_sub_queries():
    absents_subquery = Subquery(
        Attendance.objects.filter(
            member=OuterRef("pk"),
            status__in=(AttendanceStatus.ABSENT, AttendanceStatus.EXCUSED),
        )
        .values("member")
        .annotate(cnt=Count("id"))
        .values("cnt")
    )

    tasks_sent_subquery = Subquery(
        ReciviedTask.objects.filter(member=OuterRef("pk"))
        .values("member")
        .annotate(cnt=Count("id"))
        .values("cnt")
    )

    tasks_prefetch = Prefetch(
        "tasks_sent",
        queryset=ReciviedTask.objects.select_related(
            "task",
            "track",
        ).prefetch_related("files"),
        to_attr="tasks_prefetched",
    )

    return (
        Member.objects.select_related("track", "bdaya_user")
        .prefetch_related(tasks_prefetch)
        .annotate(
            absents=Coalesce(absents_subquery, 0),
            total_tasks_sent=Coalesce(tasks_sent_subquery, 0),
            total_tasks=Count("track__tasks"),
        )
        .annotate(
            missing_tasks=ExpressionWrapper(
                F("total_tasks") - F("total_tasks_sent"),
                output_field=PositiveSmallIntegerField(),
            ),
        )
    )


@bolt.get("/profile/{member_code}/", response_model=MemberProfileMSGSerializer)
async def get_profile(member_code: str, user: BdayaUser = Depends(get_any_authenticated_user)):  # type: ignore
    """get member profile
    
    if the requested user is a `member` the `member_code` parameter is ignored
    
    else then it uses the `member_code` parameter
    """
    
    if user.is_member:  # type: ignore
        target_code = user.member.code  # type: ignore
    else:
        target_code = member_code

    if cached_data := await cache.aget(member_profile_cache_key(target_code)):
        return HttpResponse(cached_data, content_type=JSON_CONTENT_TYPE)

    query = get_sub_queries()

    try:
        member = await aget_object_or_404(query, code=target_code)
    except:
        raise NotFound(detail=f"Member with code {member_code} not found")

    data = MemberProfileMSGSerializer.from_model(member)
    encoded_data = data.encode()
    await cache.aset(
        member_profile_cache_key(data.code), encoded_data, 1800
    )  # 30 minutes

    return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

@bolt.get("/edit-task/{sent_task_id}/", response_model=RecivedTaskMSGSerializer)
async def get_editable_task(sent_task_id: IntId, user: BdayaUser = Depends(get_member_user)):  # type: ignore
    """get the signed task to edit
    
    it allows the `member` to get the task that he sent to edit it
    """
    
    try:
        task = await (
            ReciviedTask.objects.select_related("task", "member__bdaya_user", "track")
            .prefetch_related("files")
            .defer(
                "task__track",
                "member__collage_code",
                "member__bonus",
                "member__track",
                "member__joined_at",
                "member__status",
            )
            .aget(id=sent_task_id, member__code=user.member.code)  # type: ignore
        )
    except ReciviedTask.DoesNotExist:
        raise NotFound(detail=f"Recived Task with id {sent_task_id} does not exists")

    task_serialized_encoded = RecivedTaskMSGSerializer.from_model(task).encode()
    return HttpResponse(task_serialized_encoded, content_type=JSON_CONTENT_TYPE)

@bolt.put("/edit-task/{sent_task_id}/", status_code=204)
async def update_my_task(sent_task_id: IntId, notes: FormStr, files: Annotated[list[UploadFile], File(alias='files')] = [], user: BdayaUser = Depends(get_member_user)): # type: ignore
    """send task edits
    
    once the `member` finish editing and sends it here it marks the task to be `signed=False`
    """
    
    try:
        task = await (
            ReciviedTask.objects
            .only("notes", "signed", "member__code", "task_id")
            .select_related("member", "task")
            .aget(id=sent_task_id, member__bdaya_user__email=user.email) # type: ignore
        )
    except ReciviedTask.DoesNotExist:
        raise NotFound(detail=f"Recived Task with id {sent_task_id} does not exists")
    
    update_fields: set[str] = {"signed"}

    @sync_to_async
    def safe_transaction() -> None:
        needs_save: bool = False
        with transaction.atomic():
            if notes is not None:
                task.notes = notes
                update_fields.add("notes")
                needs_save = True

            if files:
                ReciviedTaskFile.objects.filter(recivied_task=task).delete()
                task_files = (
                    ReciviedTaskFile(recivied_task=task, file=file.file)
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

    return Response(status.HTTP_204_NO_CONTENT)

@bolt.get("/protected_media/tasks/{sent_task_id}/")
async def get_protected_file(sent_task_id: IntId, user: BdayaUser = Depends(get_any_authenticated_user)): # type: ignore
    """access a protected file
    
    it check if the requested user is an `organizer` or `technical` to get the file
    
    or check if the user is a `member` and it's the same `member` that uplouded this task to get open the file
    """
    
    try:
        document = await ReciviedTaskFile.objects \
            .only("id", 'file', "file_name", "recivied_task__member__bdaya_user__email") \
            .select_related('recivied_task__member__bdaya_user') \
            .aget(id=sent_task_id)
    except ReciviedTaskFile.DoesNotExist:
        raise NotFound(detail=f"File with recived task id {sent_task_id} does not exists")
    
    # check if it's an organizer or technical to get the file or check if the user is a member and it's the same member that uplouded this task
    if (user.is_member and document.recivied_task.member.bdaya_user.email != user.email):
        raise NotFound()

    content_type, _ = mimetypes.guess_type(document.file.url)

    nginx_url = quote(f"/api/media/{document.file.name}")
    final_content_type = content_type or 'application/octet-stream'

    disposition_type = 'inline' if final_content_type in SAFE_MIMETYPES else 'attachment'

    response = HttpResponse(b"", content_type=final_content_type)
    response['X-Accel-Redirect'] = nginx_url
    response['Content-Disposition'] = f"{disposition_type}; filename*=UTF-8''{quote(document.file_name)}"

    return response
