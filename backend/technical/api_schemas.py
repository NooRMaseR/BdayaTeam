from core.api_schemas import SimpleTrackSchema
from member.models import MemberStatus
from pydantic import EmailStr
from datetime import datetime
from ninja import Schema
from . import models

class TaskCreateRequest(Schema):
    task_number: int
    expires_at: datetime
    description: str
    
class TaskAlreadyExistsError(Schema):
    task_number: str = "This task number already exists"
    
class TaskSignRequest(Schema):
    degree: int
    technical_notes: str

class SimpleTaskResponse(Schema):
    id: int
    task_number: int

class SimpleRecivedTaskResponse(Schema):
    id: int
    task: SimpleTaskResponse
    member_code: str
    notes: str | None = None
    technical_notes: str | None = None
    degree: int | None = None
    
class TechnicalMembersResponse(Schema):
    code: str
    name: str
    email: EmailStr
    collage_code: str
    phone_number: str
    bonus: int
    track: SimpleTrackSchema
    status: MemberStatus
    tasks: list[SimpleRecivedTaskResponse]
    
class TechnicalMembersTasksUpdateRequest(Schema):
    task_id: int
    code: str
    value: int | str
    field: models.MemberTechEditType
