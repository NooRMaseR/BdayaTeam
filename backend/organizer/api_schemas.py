from typing import Any, Literal, TypedDict
from django_bolt import UploadFile
from datetime import date

from django_bolt.serializers import Serializer, field_validator
from . import models
import msgspec
import ast

class DayRequestMSG(msgspec.Struct):
    day: date

class DayUpdateRequestMSG(msgspec.Struct):
    oldDay: date
    newDay: date

class AttendanceDayResponseMSG(msgspec.Struct):
    id: int
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
    # organizer_can_edit: list[str] = []
    organizer_can_edit: str | None = None
    site_image: UploadFile | None = None
    hero_image: UploadFile | None = None
    
    @field_validator("organizer_can_edit", 'before')
    def transform_organizer_can_edit(cls, v: str):
        try:
            conveted_list = ast.literal_eval(v)
            if isinstance(conveted_list, list):
                return conveted_list
        except:
            raise ValueError("a list[str] converted as string is required")

class OrganizerBroudCastData(TypedDict):
    by: str
    code: str
    changedKey: str
    changedValue: Any
    
class OrganizerBroudCast(TypedDict):
    type: Literal["edit"]
    data: OrganizerBroudCastData
