from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskCommentCreate(BaseModel):
    content: str
    author_id: Optional[UUID] = None

class TaskCommentOut(BaseModel):
    id: UUID
    task_id: UUID
    author_id: Optional[UUID]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
