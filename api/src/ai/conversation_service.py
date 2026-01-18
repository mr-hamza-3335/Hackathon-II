"""
Conversation History Management Service.
Phase III: AI Chatbot - Persistent conversation history

Handles loading and saving conversation history from/to PostgreSQL.
"""
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from ..models.conversation import Conversation
from ..models.message import Message


class ConversationService:
    """
    Service for managing conversation history.
    All state is persisted in PostgreSQL.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize with database session.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db

    async def get_or_create_conversation(self, user_id: str) -> Conversation:
        """
        Get the most recent conversation for a user or create a new one.

        Args:
            user_id: UUID of the user

        Returns:
            Conversation instance
        """
        # Try to find existing conversation
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == UUID(user_id))
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            # Create new conversation
            conversation = Conversation(user_id=UUID(user_id))
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)

        return conversation

    async def get_conversation_by_id(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by ID (with user authorization).

        Args:
            conversation_id: UUID of the conversation
            user_id: UUID of the user (for authorization)

        Returns:
            Conversation if found and authorized, None otherwise
        """
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.id == UUID(conversation_id),
                Conversation.user_id == UUID(user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_history(self, conversation_id: str, limit: int = 50) -> List[dict]:
        """
        Load conversation history from database.

        Args:
            conversation_id: UUID of the conversation
            limit: Maximum number of messages to load

        Returns:
            List of message dictionaries for OpenAI API
        """
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == UUID(conversation_id))
            .order_by(Message.created_at)
            .limit(limit)
        )
        messages = result.scalars().all()

        # Convert to API message format
        history = []
        for msg in messages:
            message_dict = {
                "role": msg.role,
                "content": msg.content
            }

            # Include tool calls if present (for assistant messages)
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls

            history.append(message_dict)

        return history

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None,
        tool_results: Optional[dict] = None
    ) -> Message:
        """
        Save a message to the conversation.

        Args:
            conversation_id: UUID of the conversation
            role: Message role ('user', 'assistant', or 'system')
            content: Message text content
            tool_calls: Tool calls made (for assistant messages)
            tool_results: Tool execution results

        Returns:
            Created Message instance
        """
        message = Message(
            conversation_id=UUID(conversation_id),
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(message)

        # Update conversation's updated_at timestamp
        await self.db.execute(
            update(Conversation)
            .where(Conversation.id == UUID(conversation_id))
            .values(updated_at=datetime.now(timezone.utc))
        )

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def save_user_message(self, conversation_id: str, content: str) -> Message:
        """
        Save a user message.

        Args:
            conversation_id: UUID of the conversation
            content: User's message text

        Returns:
            Created Message instance
        """
        return await self.save_message(
            conversation_id=conversation_id,
            role="user",
            content=content
        )

    async def save_assistant_message(
        self,
        conversation_id: str,
        content: str,
        tool_calls: Optional[dict] = None,
        tool_results: Optional[dict] = None
    ) -> Message:
        """
        Save an assistant message.

        Args:
            conversation_id: UUID of the conversation
            content: Assistant's response text
            tool_calls: Tool calls made during processing
            tool_results: Results of tool calls

        Returns:
            Created Message instance
        """
        return await self.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results
        )

    async def get_message_count(self, conversation_id: str) -> int:
        """
        Get the number of messages in a conversation.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Number of messages
        """
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(Message.conversation_id == UUID(conversation_id))
        )
        return result.scalar() or 0

    async def clear_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Clear all messages in a conversation (with authorization).

        Args:
            conversation_id: UUID of the conversation
            user_id: UUID of the user (for authorization)

        Returns:
            True if cleared successfully, False if not found/authorized
        """
        # Verify ownership
        conversation = await self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return False

        # Delete all messages
        from sqlalchemy import delete
        await self.db.execute(
            delete(Message).where(Message.conversation_id == UUID(conversation_id))
        )
        await self.db.commit()

        return True
