from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from .base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum("backlog", "todo", "in_progress", "peer_review", "final_review", "done", name="task_status"), default="backlog")
    priority = Column(Enum("low", "medium", "high", "critical", name="task_priority"), default="medium")
    story_points = Column(Integer, default=1)
    sprint_id = Column(UUID(as_uuid=True), ForeignKey("sprints.id"))
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    deadline = Column(DateTime(timezone=True))