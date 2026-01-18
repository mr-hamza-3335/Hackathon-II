"""
Message ORM model for chat messages within conversations.
Phase III: AI Chatbot - Conversation history persistence
"""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, ForeignKey, CheckConstraint, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class Message(Base):
    """
    Represents a single message in a conversation.

    Attributes:
        id: UUID primary key
        conversation_id: Foreign key to conversation
        role: Message role ('user', 'assistant', or 'system')
        content: Message text content
        tool_calls: JSON of tool calls made (for assistant messages)
        tool_results: JSON of tool execution results
        created_at: Message timestamp

    Messages store the full conversation history including tool interactions.
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSONB, nullable=True)
    tool_results = Column(JSONB, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship: Each message belongs to one conversation
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="messages_valid_role"),
        Index("idx_messages_conversation_id", "conversation_id"),
        Index("idx_messages_created_at", "conversation_id", "created_at"),
    )

    def __repr__(self) -> str:
        content_preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"<Message(id={self.id}, role={self.role}, content={content_preview})>"

    def to_dict(self) -> dict:
        """Convert message to dictionary for API response."""
        return {
            "id": str(self.id),
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
