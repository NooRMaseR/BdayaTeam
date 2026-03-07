from core.serializers import BaseMSGSerializer
from datetime import datetime
from .models import Task
from typing import Self
    
class TaskSmallMSGSerializer(BaseMSGSerializer[Task], frozen=True):
    id: int
    task_number: int

    @classmethod
    def from_model(cls, model: Task) -> Self:
        return cls(
            model.pk,
            model.task_number
        )


class TaskMSGSerializer(TaskSmallMSGSerializer, frozen=True):
    created_at: datetime
    expires_at: datetime
    description: str
    expired: bool
    unsigned_tasks_count: int = 0
    
    @classmethod
    def from_model(cls, model: Task) -> Self:
        return cls(
            id=model.pk,
            task_number=model.task_number,
            created_at=model.created_at,
            expires_at=model.expires_at,
            description=model.description,
            expired=model.is_expired,
        )

