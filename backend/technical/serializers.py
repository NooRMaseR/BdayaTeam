from core.serializers import BaseMSGSerializer, TrackNameOnlyMSGSerializer
from member.models import AllowedTrackFileExtention
from django_bolt.serializers import HttpsURL
from datetime import datetime
from .models import Task
from utils import IntId
from typing import Self

class TaskSmallMSGSerializer(BaseMSGSerializer[Task], frozen=True):
    id: IntId
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
    images: list[str] = []
    links: list[HttpsURL] = []
    # links: list[str] = []
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
            links=model.links if model.links else [],
            images=[image.image.url for image in model.images.all()], # type: ignore
        )


class TrackExtenstionsSerializer(BaseMSGSerializer[AllowedTrackFileExtention], frozen=True):
    track: TrackNameOnlyMSGSerializer
    extensions: list[str] = []

    @classmethod
    def from_model(cls, model: AllowedTrackFileExtention) -> Self:
        return cls(
            track=TrackNameOnlyMSGSerializer.from_model(model.track),
            extensions=model.extensions
        )
