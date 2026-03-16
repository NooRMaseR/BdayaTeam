
def technical_tasks_cache_key(track_name: str) -> str:
    return f"technical_tasks:t{track_name}"

def tasks_from_memebrs_cache_key(track_name: str, task_id: int) -> str:
    return f"technical_recived_tasks_{track_name}:i{task_id}"

def task_view_cache_key(task_id: int) -> str:
    return f"task_view:i{task_id}"

def members_by_technicals_cache_key(track_name: str) -> str:
    return f"members_tech_{track_name}"