from datetime import date
import msgspec

class AttendanceDayMSGSerializer(msgspec.Struct):
    id: int
    day: date
    
class AttendanceMSGSerializer(msgspec.Struct):
    date: list[AttendanceDayMSGSerializer]
    status: str
    excuse_reason: str
    
class SiteSettingsImagesMSGSerializer(msgspec.Struct):
    site_image: str
    hero_image: str
    
class SiteSettingsMSGSerializer(msgspec.Struct):
    site_image: str
    hero_image: str
    is_register_enabled: bool
    organizer_can_edit: list[str] = []
    