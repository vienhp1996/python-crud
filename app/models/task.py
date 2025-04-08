import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.mixins import AuditMixin
from app.core.database import Base


class Task(AuditMixin, Base):
    __tablename__ = "task"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    score = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task(title={self.title}, score={self.score})>"
