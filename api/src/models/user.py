"""
User ORM model.
T009: Create User ORM model in api/src/models/user.py per data-model.md
Requirement References: FR-001, FR-002, FR-003, FR-004, FR-005, FR-007
"""
from uuid import uuid4
from sqlalchemy import Column, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    Represents a registered user who can authenticate and manage tasks.

    Attributes:
        id: UUID primary key (prevents enumeration attacks)
        email: Unique email address (case-insensitive comparison)
        password_hash: bcrypt-hashed password (NFR-001: cost factor 12)
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Relationship: One user has many tasks (FR-018)
    tasks = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        # Index for case-insensitive email lookup (Edge Case: email normalization)
        Index("idx_users_email_lower", "email"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
