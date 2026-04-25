import msgspec
from utils import IntId
    
class TaskRequestMSG(msgspec.Struct):
    task_id: IntId
    notes: str | None = None

class TaskSubmitRequestMSG(msgspec.Struct):
    task_id: IntId
    notes: str | None = None
