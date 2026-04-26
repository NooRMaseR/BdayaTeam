from django.utils import timezone
from datetime import datetime
from core.serializers import TrackNameOnlyMSGSerializer
from utils import IntId
from . import models
import msgspec

class TaskCreateRequestMSG(msgspec.Struct):
    task_number: IntId
    expires_at: datetime
    description: str
    
    def __post_init__(self) -> None:
        if self.expires_at <= timezone.now():
            raise msgspec.ValidationError("expires_at cannot be in the past")

class TaskSignRequestMSG(msgspec.Struct):
    degree: int
    technical_notes: str

class TechnicalMembersTasksUpdateRequestMSG(msgspec.Struct):
    task_id: IntId
    code: str
    value: int | str
    field: models.MemberTechEditType

class TrackExtensionsRequestMSG(msgspec.Struct):
    extensions: list[str] = []
