from datetime import date
from typing import Self

from core.serializers import BaseMSGSerializer
from .models import Attendance, AttendanceAllowedDay, SiteSetting

class AttendanceDayMSGSerializer(BaseMSGSerializer[AttendanceAllowedDay], frozen=True):
    id: int
    day: date

    @classmethod
    def from_model(cls, model: AttendanceAllowedDay) -> Self:
        return cls(
            model.pk,
            model.day
        )

    
class AttendanceMSGSerializer(BaseMSGSerializer[Attendance], frozen=True):
    date: AttendanceDayMSGSerializer
    status: str
    excuse_reason: str | None = None
    
    @classmethod
    def from_model(cls, model: Attendance) -> Self:
        return cls(
            date=AttendanceDayMSGSerializer.from_model(model.date),
            status=model.status,
            excuse_reason=model.excuse_reason
        )

    
class SiteSettingsImagesMSGSerializer(BaseMSGSerializer[SiteSetting], frozen=True):
    site_image: str | None
    hero_image: str | None

    @classmethod
    def from_model(cls, model: SiteSetting) -> Self:
        return cls(
            model.site_image.url if model.site_image else None,
            model.hero_image.url if model.hero_image else None
        )

    
class SiteSettingsMSGSerializer(SiteSettingsImagesMSGSerializer, frozen=True):
    is_register_enabled: bool
    organizer_can_edit: list[str] = []
    
    @classmethod
    def from_model(cls, model: SiteSetting) -> Self:
        return cls(
            site_image=model.site_image.url if model.site_image else None,
            hero_image=model.hero_image.url if model.hero_image else None,
            is_register_enabled=model.is_register_enabled,
            organizer_can_edit=model.organizer_can_edit,
        )
    