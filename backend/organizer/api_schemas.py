from typing import Annotated, Any, Literal, TypedDict
from datetime import date
from . import models
import msgspec

class DayRequestMSG(msgspec.Struct):
    day: date

class DayUpdateRequestMSG(msgspec.Struct):
    oldDay: date
    newDay: date

class AttendanceDayResponseMSG(msgspec.Struct):
    id: Annotated[int, msgspec.Meta(gt=0)]
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

class OrganizerBroudCastData(TypedDict):
    by: str
    code: str
    changedKey: str
    changedValue: Any
    
class OrganizerBroudCast(TypedDict):
    type: Literal["edit"]
    data: OrganizerBroudCastData
