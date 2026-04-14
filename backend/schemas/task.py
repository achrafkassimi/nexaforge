from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    story_points: Optional[int] = 1
    sprint_id: UUID
    assignee_id: Optional[UUID] = None
    deadline: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    story_points: Optional[int] = None
    sprint_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    deadline: Optional[datetime] = None

class TaskOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    story_points: int
    sprint_id: UUID
    assignee_id: Optional[UUID]
    deadline: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}