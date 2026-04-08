from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AgentCreate(BaseModel):
    name: str
    agent_type: str

class AgentOut(BaseModel):
    id: UUID
    name: str
    agent_type: str
    status: str
    is_active: bool
    current_task_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}