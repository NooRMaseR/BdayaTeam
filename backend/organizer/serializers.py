from datetime import date
from .models import AttendanceStatus
from django_bolt.serializers import Serializer
from core.serializers import ExtraSerialization

class AttendanceDayMSGSerializer(Serializer, ExtraSerialization):
    id: int
    day: date

class AttendanceMSGBy(Serializer, ExtraSerialization):
    id: int
    username: str
    
class AttendanceMSGSerializer(Serializer, ExtraSerialization):
    date: AttendanceDayMSGSerializer
    status: AttendanceStatus
    by: AttendanceMSGBy
    excuse_reason: str | None = None

    
class SiteSettingsImagesMSGSerializer(Serializer, ExtraSerialization):
    site_image: str | None = None
    hero_image: str | None = None

    
class SiteSettingsMSGSerializer(SiteSettingsImagesMSGSerializer):
    is_register_enabled: bool = False
    organizer_can_edit: list[str] = []

    