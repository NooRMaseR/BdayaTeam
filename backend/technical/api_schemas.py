from django.utils import timezone
from datetime import datetime
from typing import Annotated
from . import models
import msgspec

class TaskCreateRequestMSG(msgspec.Struct):
    task_number: Annotated[int, msgspec.Meta(gt=0)]
    expires_at: datetime
    description: str
    
    def __post_init__(self) -> None:
        if self.expires_at <= timezone.now():
            raise msgspec.ValidationError("expires_at cannot be in the past")

class TaskSignRequestMSG(msgspec.Struct):
    degree: str | int
    technical_notes: str

class TechnicalMembersTasksUpdateRequestMSG(msgspec.Struct):
    task_id: Annotated[int, msgspec.Meta(gt=0)]
    code: str
    value: int | str
    field: models.MemberTechEditType
