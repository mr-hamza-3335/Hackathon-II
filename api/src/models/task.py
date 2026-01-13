"""
Task ORM model.
T010: Create Task ORM model in api/src/models/task.py per data-model.md
Requirement References: FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018
"""
from uuid import uuid4
from sqlalchemy import Column, String, Boolean, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Task(Base, TimestampMixin):
    """
    Represents a todo item owned by a user.

    Attributes:
        id: UUID primary key (FR-010: auto-generated unique ID)
        user_id: Foreign key to user (FR-018: associated with owner)
        title: Task description 1-500 chars (FR-016)
        completed: Completion status (FR-012, FR-013)

    Security: All queries MUST include user_id filter (FR-008)
    """
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(500), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)

    # Relationship: Each task belongs to one user
    user = relationship("User", back_populates="tasks")

    __table_args__ = (
        # Ensure title is not empty (FR-016)
        CheckConstraint("LENGTH(TRIM(title)) > 0", name="tasks_title_not_empty"),
        # Index for user's task list queries (FR-008, FR-011)
        Index("idx_tasks_user_id", "user_id"),
        # Composite index for filtered queries
        Index("idx_tasks_user_completed", "user_id", "completed"),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title[:20]}..., completed={self.completed})>"
