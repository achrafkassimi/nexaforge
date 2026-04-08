from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class SprintCreate(BaseModel):
    name: str
    goal: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    project_id: UUID

class SprintOut(BaseModel):
    id: UUID
    name: str
    goal: Optional[str]
    status: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    velocity: int
    project_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}