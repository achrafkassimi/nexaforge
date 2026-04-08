from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from .base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum("draft", "active", "review", "done", "archived", name="project_status"), default="draft")
    priority = Column(Enum("low", "medium", "high", "critical", name="priority_level"), default="medium")
    deadline = Column(DateTime(timezone=True))
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))