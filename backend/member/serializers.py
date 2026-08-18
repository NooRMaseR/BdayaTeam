from technical.serializers import TaskMSGSerializer, TaskSmallMSGSerializer
from core.serializers import TrackNameOnlyMSGSerializer, ExtraSerialization
from django_bolt.serializers import Serializer, field_validator
from organizer.serializers import AttendanceMSGSerializer

from .models import MemberStatus
from datetime import datetime

class MemberBaseMSG(Serializer, ExtraSerialization):
    code: str
    name: str
    email: str
    collage_code: str
    phone_number: str
    bonus: int
    track: TrackNameOnlyMSGSerializer
    status: MemberStatus
    
    @field_validator('phone_number', 'before')
    @classmethod
    def transform_phone_number(cls, v) -> str:
        return str(v)


class MemberORGMSGSerializer(MemberBaseMSG):
    attendances: list[AttendanceMSGSerializer] = []

class SignedMSGBy(Serializer, ExtraSerialization):
    id: int
    username: str

class RecivedTaskSmallMSGSerializer(Serializer, ExtraSerialization):
    id: int
    task: TaskSmallMSGSerializer
    member_code: str
    signed_by: SignedMSGBy | None = None
    notes: str | None = None
    technical_notes: str | None = None
    degree: int | None = None


class MemberTechnicalMSGSerializer(MemberBaseMSG):
    tasks: list[RecivedTaskSmallMSGSerializer] = []


class MemberMSGSerializerForTask(Serializer, ExtraSerialization):
    code: str
    name: str

class RecivedFile(Serializer, ExtraSerialization):
    id: int
    file: str
    file_name: str

class RecivedTaskMSGSerializer(Serializer, ExtraSerialization):
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


class MemberProfileMSGSerializer(Serializer, ExtraSerialization):
    absents: int
    track: TrackNameOnlyMSGSerializer
    total_tasks_sent: int
    missing_tasks: int
    name: str
    code: str
    status: str
    tasks: list[RecivedTaskMSGSerializer] = []

