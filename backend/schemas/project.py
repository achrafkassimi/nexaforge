from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cahier_de_charge: Optional[str] = None
    priority: Optional[str] = "medium"
    deadline: Optional[datetime] = None

class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    cahier_de_charge: Optional[str]
    rejection_note: Optional[str]
    status: str
    priority: str
    deadline: Optional[datetime]
    manager_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}
