from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from .base import Base

class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    goal = Column(String)
    status = Column(Enum("planned", "active", "closed", name="sprint_status"), default="planned")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    velocity = Column(Integer, default=0)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))