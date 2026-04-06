from pydantic import EmailStr, PositiveInt, field_validator, NonNegativeInt
from core.api_schemas import SimpleTrackSchema
from member.models import MemberStatus
from django.utils import timezone
from datetime import datetime
from ninja import Schema
from . import models

class TaskCreateRequest(Schema):
    task_number: PositiveInt
    expires_at: datetime
    description: str
    
    @field_validator('expires_at', mode='after')
    @classmethod
    def validate_expires_at(cls, v: datetime) -> datetime:
        if v <= timezone.now():
            raise ValueError("expires_at cannot be in the past")
        
        return v
            
    
class TaskAlreadyExistsError(Schema):
    task_number: str = "This task number already exists"
    
class TaskSignRequest(Schema):
    degree: NonNegativeInt
    technical_notes: str

class SimpleTaskResponse(Schema):
    id: PositiveInt
    task_number: int

class SignedBy(Schema):
    id: PositiveInt
    username: str

class SimpleRecivedTaskResponse(Schema):
    id: PositiveInt
    task: SimpleTaskResponse
    member_code: str
    notes: str | None = None
    technical_notes: str | None = None
    signed_by: SignedBy | None = None
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
    task_id: PositiveInt
    code: str
    value: int | str
    field: models.MemberTechEditType
