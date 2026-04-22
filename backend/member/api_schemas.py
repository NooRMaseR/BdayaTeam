from typing import Annotated
import msgspec
    
class TaskRequestMSG(msgspec.Struct):
    task_id: Annotated[int, msgspec.Meta(gt=0)]
    notes: str | None = None
