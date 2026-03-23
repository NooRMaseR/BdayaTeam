from technical.serializers import TaskMSGSerializer, TaskSmallMSGSerializer
from core.serializers import TrackNameOnlyMSGSerializer, BaseMSGSerializer
from organizer.serializers import AttendanceMSGSerializer

from .models import Member, ReciviedTask, ReciviedTaskFile
from collections.abc import Iterable
from datetime import datetime
from typing import Self


class MemberBaseMSG(BaseMSGSerializer[Member], frozen=True):
    code: str
    name: str
    email: str
    collage_code: str
    phone_number: str
    bonus: int
    track: TrackNameOnlyMSGSerializer
    status: str


class MemberORGMSGSerializer(MemberBaseMSG, frozen=True):
    attendances: list[AttendanceMSGSerializer] = []

    @classmethod
    def from_model(cls, model: Member) -> Self:
        return cls(
            code=model.code,
            name=model.bdaya_user.username,
            email=model.bdaya_user.email,
            collage_code=model.collage_code,
            phone_number=model.bdaya_user.phone_number,
            status=model.status,
            bonus=model.bonus,
            track=TrackNameOnlyMSGSerializer.from_model(model.track),
            attendances=AttendanceMSGSerializer.from_queryset(model.attendances.all()),  # type: ignore
        )

    @classmethod
    def from_queryset_with_track(cls, models: Iterable[Member], track: TrackNameOnlyMSGSerializer) -> list[Self]:
        return [
            cls(
                code=model.code,
                name=model.bdaya_user.username,
                email=model.bdaya_user.email,
                collage_code=model.collage_code,
                phone_number=model.bdaya_user.phone_number,
                status=model.status,
                bonus=model.bonus,
                track=track,
                attendances=AttendanceMSGSerializer.from_queryset(model.attendances.all()),  # type: ignore
            )
            for model in models
        ]


class RecivedTaskSmallMSGSerializer(BaseMSGSerializer[ReciviedTask], frozen=True):
    id: int
    task: TaskSmallMSGSerializer
    member_code: str
    notes: str | None = None
    technical_notes: str | None = None
    degree: int | None = None

    @classmethod
    def from_model(cls, model: ReciviedTask) -> Self:
        return cls(
            id=model.pk,
            task=TaskSmallMSGSerializer.from_model(model.task),
            member_code=model.member.code,
            notes=model.notes,
            technical_notes=model.technical_notes,
            degree=model.degree,
        )


class MemberTechnicalMSGSerializer(MemberBaseMSG, frozen=True):
    tasks: list[RecivedTaskSmallMSGSerializer] = []

    @classmethod
    def from_model(cls, model: Member) -> Self:
        return cls(
            code=model.code,
            name=model.bdaya_user.username,
            email=model.bdaya_user.email,
            collage_code=model.collage_code,
            phone_number=model.bdaya_user.phone_number,
            bonus=model.bonus,
            track=TrackNameOnlyMSGSerializer.from_model(model.track),
            status=model.status,
            tasks=RecivedTaskSmallMSGSerializer.from_queryset(model.tasks_sent.all()),  # type: ignore
        )
        
    @classmethod
    def from_queryset_with_track(cls, models: Iterable[Member], track: TrackNameOnlyMSGSerializer) -> list[Self]:
        return [
            cls(
                code=model.code,
                name=model.bdaya_user.username,
                email=model.bdaya_user.email,
                collage_code=model.collage_code,
                phone_number=model.bdaya_user.phone_number,
                bonus=model.bonus,
                track=track,
                status=model.status,
                tasks=RecivedTaskSmallMSGSerializer.from_queryset(model.prefetched_tasks) # type: ignore
            )
            for model in models
        ]


class MemberMSGSerializerForTask(BaseMSGSerializer[Member], frozen=True):
    code: str
    name: str

    @classmethod
    def from_model(cls, model: Member) -> Self:
        return cls(model.code, model.bdaya_user.username)


class RecivedFile(BaseMSGSerializer[ReciviedTaskFile], frozen=True):
    id: int
    file_url: str

    @classmethod
    def from_model(cls, model: ReciviedTaskFile) -> Self:
        return cls(model.pk, model.file.url)


class RecivedTaskMSGSerializer(BaseMSGSerializer[ReciviedTask], frozen=True):
    id: int
    task: TaskMSGSerializer
    member: MemberMSGSerializerForTask
    track: TrackNameOnlyMSGSerializer
    files_url: list[RecivedFile]
    notes: str | None
    degree: int | None
    signed: bool
    recived_at: datetime
    technical_notes: str | None = None

    @classmethod
    def from_model(cls, model: ReciviedTask) -> Self:
        return cls(
            id=model.pk,
            task=TaskMSGSerializer.from_model(model.task),
            member=MemberMSGSerializerForTask.from_model(model.member),
            track=TrackNameOnlyMSGSerializer.from_model(model.track),
            files_url=RecivedFile.from_queryset(model.files.all()),  # type: ignore
            notes=model.notes,
            degree=model.degree,
            signed=model.signed,
            recived_at=model.recived_at,
            technical_notes=model.technical_notes
        )


class MemberProfileMSGSerializer(BaseMSGSerializer[Member], frozen=True):
    absents: int
    track: TrackNameOnlyMSGSerializer
    total_tasks_sent: int
    missing_tasks: int
    name: str
    code: str
    status: str
    tasks: list[RecivedTaskMSGSerializer] = []

    @classmethod
    def from_model(cls, model: Member) -> Self:
        return cls(
            absents=model.absents,  # type: ignore
            track=TrackNameOnlyMSGSerializer.from_model(model.track),
            total_tasks_sent=model.total_tasks_sent,  # type: ignore
            missing_tasks=model.missing_tasks,  # type: ignore
            name=model.bdaya_user.username,
            code=model.code,
            status=model.status,
            tasks=RecivedTaskMSGSerializer.from_queryset(model.tasks_prefetched),  # type: ignore
        )
