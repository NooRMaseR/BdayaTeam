from organizer.serializers import AttendanceMSGSerializer
from core.serializers import TrackNameOnlyMSGSerializer
from technical.serializers import TaskMSGSerializer
from datetime import datetime
import msgspec

class MemberMSGSerializer(msgspec.Struct):
    code: str
    name: str
    email: str
    collage_code: str
    phone_number: str
    bonus: int
    track: TrackNameOnlyMSGSerializer
    joined_at: datetime
    status: str
    attendances: list[AttendanceMSGSerializer] = []
    
class MemberMSGSerializerForTask(msgspec.Struct):
    code: str
    name: str
    
class RecivedFile(msgspec.Struct):
    id: int
    file_url: str

class RecivedTaskMSGSerializer(msgspec.Struct):
    id: int
    task: TaskMSGSerializer
    member: MemberMSGSerializerForTask
    track: TrackNameOnlyMSGSerializer
    files_url: list[RecivedFile]
    notes: str | None
    degree: int | None
    signed: bool
    recived_at: datetime

class MemberProfileMSGSerializer(msgspec.Struct):
    absents: int
    track: TrackNameOnlyMSGSerializer
    total_tasks_sent: int
    missing_tasks: int
    name: str
    code: str