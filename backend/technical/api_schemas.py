from django_bolt.serializers import Serializer, field_validator
from django.utils import timezone
from datetime import datetime
from utils import IntId
from . import models
import msgspec
import json

class TaskCreateRequestMSG(Serializer):
    task_number: IntId
    expires_at: datetime
    description: str
    links: str | None = None
    
    @field_validator("links", "before")
    def transform_links(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    @field_validator("expires_at", 'before')
    def validate_expires(cls, v) -> None:
        if v <= timezone.now():
            raise ValueError("expires_at cannot be in the past")

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
