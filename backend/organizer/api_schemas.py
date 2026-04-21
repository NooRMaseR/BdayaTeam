from pydantic import PositiveInt, field_validator
from typing import Annotated, Any, Literal, TypedDict
from datetime import date
from ninja import Schema
from . import models
import msgspec

class DayRequestMSG(msgspec.Struct):
    day: date

class DayRequest(Schema):
    day: date

class DayUpdateRequestMSG(msgspec.Struct):
    oldDay: date
    newDay: date

class DayUpdateRequest(Schema):
    oldDay: date
    newDay: date

class AttendanceDayResponseMSG(msgspec.Struct):
    id: Annotated[int, msgspec.Meta(gt=0)]
    day: date
    
class AttendanceDayResponse(Schema):
    id: PositiveInt
    day: date
    
class AttendanceBy(Schema):
    id: PositiveInt
    username: str

class AttendanceSmallResponse(Schema):
    date: AttendanceDayResponse
    status: models.AttendanceStatus
    by: AttendanceBy
    excuse_reason: str | None = None

class MemberEditGridRequestMSG(msgspec.Struct):
    type: models.MemberEditType
    code: str
    field: str
    value: str | int
    excuse: str | None = None

class MemberEditGridRequest(Schema):
    type: models.MemberEditType
    field: str
    value: str | int | models.AttendanceStatus
    excuse: str | None = None
    code: str

class SettingsRequest(Schema):
    is_register_enabled: bool = False
    organizer_can_edit: list[models.OrganizerEditableFields] = []
    
    @field_validator('organizer_can_edit', mode='before')
    @classmethod
    def parse_organizer_list(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        
        # check if the request contains only one item and it's a string like this 'bonus,status'
        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], str) and ',' in value[0]:
            return [item.strip() for item in value[0].split(',') if item.strip()]
                
        return value
    
class SettingsImagesResponseMSG(msgspec.Struct):
    site_image: str | None = None
    hero_image: str | None = None
    
class SettingsImagesResponse(Schema):
    site_image: str | None
    hero_image: str | None
    
class SettingsResponse(SettingsImagesResponse):
    is_register_enabled: bool
    organizer_can_edit: list[models.OrganizerEditableFields]
   
class OrganizerBroudCastData(TypedDict):
    by: str
    code: str
    changedKey: str
    changedValue: Any
    
class OrganizerBroudCast(TypedDict):
    type: Literal["edit"]
    data: OrganizerBroudCastData
