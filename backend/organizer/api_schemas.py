from typing import Any, Literal, TypedDict
from django_bolt import UploadFile
from datetime import date

from django_bolt.serializers import PositiveInt, Serializer, field_validator
from . import models
import msgspec
import ast

class DayRequestMSG(msgspec.Struct):
    day: date

class DayUpdateRequestMSG(msgspec.Struct):
    oldDay: date
    newDay: date

class AttendanceDayResponseMSG(msgspec.Struct):
    id: PositiveInt
    day: date

class MemberEditGridRequestMSG(msgspec.Struct):
    type: models.MemberEditType
    code: str
    field: str
    value: str | int
    excuse: str | None = None
    
class SettingsImagesResponseMSG(msgspec.Struct):
    site_image: str | None = None
    hero_image: str | None = None

class UpdateSettingsRequestMSG(Serializer):
    is_register_enabled: bool = False
    organizer_can_edit: list[str] = []
    site_image: UploadFile | None = None
    hero_image: UploadFile | None = None

class OrganizerBroudCastData(TypedDict):
    by: str
    code: str
    changedKey: str
    changedValue: Any
    
class OrganizerBroudCast(TypedDict):
    type: Literal["edit"]
    data: OrganizerBroudCastData
