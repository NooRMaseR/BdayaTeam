from datetime import datetime
import msgspec

class TaskMSGSerializer(msgspec.Struct):
    id: int
    task_number: int
    created_at: datetime
    expires_at: datetime
    description: str
    expired: bool

