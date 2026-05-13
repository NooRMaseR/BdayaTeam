from django_bolt.serializers import Serializer
from django_bolt import UploadFile
import msgspec

class TaskSubmitRequestMSG(Serializer):
    task_id: int
    notes: str | None = None
    files: list[UploadFile] = []

class TaskUpdateRequestMSG(msgspec.Struct):
    notes: str | None = None
    files: list[UploadFile] = []
