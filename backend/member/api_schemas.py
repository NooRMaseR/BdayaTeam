from organizer.api_schemas import AttendanceSmallResponse
from core.api_schemas import SimpleTrackSchema
from datetime import datetime
from pydantic import EmailStr
from ninja import Schema
from . import models

class MemebrResponse(Schema):
    track: SimpleTrackSchema
    attendances: list[AttendanceSmallResponse]
    name: str
    email: EmailStr
    phone_number: str
    code: str
    collage_code: str
    bonus: int
    status: models.MemberStatus
    
    class Meta:
        model = models.Member
        exclude = ('joined_at',)
        
class TaskResponse(Schema):
    id: int
    task_number: int
    created_at: datetime
    expires_at: datetime
    description: str
    expired: bool
    unsigned_tasks_count: int
    
class TaskRequest(Schema):
    task_id: int
    notes: str | None = None
    
class MemberProfileName(Schema):
    code: str
    name: str
    
class RecivedFileResponse(Schema):
    id: int
    file: str
    file_name: str

class RecivedTaskMember(Schema):
    id: int
    task: TaskResponse
    member: MemberProfileName
    track: SimpleTrackSchema
    files_url: list[RecivedFileResponse]
    notes: str | None = None
    degree: int
    signed: bool
    recived_at: datetime
    technical_notes: str | None = None

class MemberProfileResponse(Schema):
    absents: int
    track: SimpleTrackSchema
    total_tasks_sent: int
    missing_tasks: int
    name: str
    code: str
    status: models.MemberStatus
    tasks: list[RecivedTaskMember]
    
class MemberTaskUpdateRequest(Schema):
    notes: str
