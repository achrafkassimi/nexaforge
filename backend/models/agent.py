from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from .base import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    agent_type = Column(Enum("backend", "frontend", "database", "devops", "manager", name="agent_type"), nullable=False)
    status = Column(Enum("idle", "working", "blocked", name="agent_status"), default="idle")
    is_active = Column(Boolean, default=True)
    current_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))