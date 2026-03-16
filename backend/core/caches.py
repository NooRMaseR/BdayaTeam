from typing import Final

TRACKS_CACHE_KEY: Final = "tracks"

def track_cache_key(track_name: str) -> str:
    return f"Track:{track_name}"