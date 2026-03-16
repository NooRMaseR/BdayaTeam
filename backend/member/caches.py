
def tasks_cache_key(track_name: str, member_id: int) -> str:
    return f"member_tasks:t{track_name}:i{member_id}"

def member_profile_cache_key(code: str) -> str:
    return f"member_profile_{code}"