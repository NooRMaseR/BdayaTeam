from core.serializers import ExtraSerialization, TrackNameOnlyMSGSerializer
from django_bolt.serializers import HttpsURL, Serializer
from datetime import datetime

class TaskSmallMSGSerializer(Serializer, ExtraSerialization):
    id: int
    task_number: int

class TaskMSGSerializer(TaskSmallMSGSerializer):
    created_at: datetime
    expires_at: datetime
    description: str
    expired: bool
    images: list[str] = []
    links: list[HttpsURL] = []
    unsigned_tasks_count: int = 0
    can_recive_tasks_after_expiration: bool = False

class TrackExtenstionsSerializer(Serializer, ExtraSerialization):
    track: TrackNameOnlyMSGSerializer
    extensions: list[str] = []
