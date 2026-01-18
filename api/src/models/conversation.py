"""
Conversation ORM model for persistent chat history.
Phase III: AI Chatbot - Conversation history persistence
"""
from uuid import uuid4
from sqlalchemy import Column, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Conversation(Base, TimestampMixin):
    """
    Represents a chat conversation session for a user.

    Attributes:
        id: UUID primary key
        user_id: Foreign key to user (owner of conversation)
        messages: Related messages in this conversation

    Conversations persist across server restarts and can be resumed.
    """
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship: One conversation has many messages
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Message.created_at",
    )

    # Relationship: Each conversation belongs to one user
    user = relationship("User", backref="conversations")

    __table_args__ = (
        Index("idx_conversations_user_id", "user_id"),
        Index("idx_conversations_updated_at", "user_id", "updated_at"),
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"
