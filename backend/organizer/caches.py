from typing import Final

SETTINGS_CACHE_KEY: Final = "settings"

def members_by_organizer_cache_key(track_name: str) -> str:
    return f"members_org_{track_name}"

def attendance_cache_key(track: str) -> str:
    return f"attendance_days_{track}"
