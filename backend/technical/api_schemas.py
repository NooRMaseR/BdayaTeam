from django_bolt.serializers import PositiveInt, Serializer, field_validator
from django_bolt import UploadFile
from django.utils import timezone
from datetime import datetime
from . import models
import msgspec
import json

class TaskCreateRequestMSG(Serializer):
    task_number: PositiveInt
    expires_at: datetime
    description: str
    # links: list[HttpsURL] = []
    links: str | None = None
    images: list[UploadFile] = []
    
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
    task_id: PositiveInt
    code: str
    value: int | str
    field: models.MemberTechEditType

class TrackExtensionsRequestMSG(msgspec.Struct):
    extensions: list[str] = []
