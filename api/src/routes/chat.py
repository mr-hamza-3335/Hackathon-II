"""
Chat API Route Handler.
Phase III: AI Chatbot - POST /api/{user_id}/chat endpoint

Implements the stateless chat endpoint that:
- Loads conversation history from PostgreSQL
- Processes messages with Cohere AI (FREE tier)
- Saves new messages to database
- Returns natural language responses with tool actions
- Works in DEMO MODE when API key is missing
"""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..middleware.auth import get_current_user
from ..db.connection import get_db
from ..ai.agent import get_agent, AgentResult
from ..ai.conversation_service import ConversationService
from ..ai.sanitizer import InputSanitizer
from ..config import get_settings

router = APIRouter(tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request with user message."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's natural language message"
    )


class ActionTaken(BaseModel):
    """Action taken by the agent."""
    tool: str = Field(..., description="Tool name that was called")
    result: dict = Field(..., description="Result of the tool call")


class ChatResponse(BaseModel):
    """Chat response with agent reply and actions."""
    response: str = Field(..., description="Agent's natural language response")
    actions_taken: List[ActionTaken] = Field(
        default=[],
        description="List of tools called during processing"
    )
    conversation_id: str = Field(..., description="UUID of the conversation")
    demo_mode: bool = Field(default=False, description="Whether running in demo mode")


@router.post(
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    summary="Chat with AI Assistant",
    description="""
    Send a natural language message to the AI assistant.

    The assistant can help manage tasks:
    - Add new tasks
    - List tasks (all, completed, or incomplete)
    - Mark tasks as complete
    - Update task titles
    - Delete tasks

    Conversation history is persisted and can be resumed after server restart.
    Works in DEMO MODE when Cohere API key is not configured.
    """,
    responses={
        200: {"description": "Successful response with AI reply"},
        400: {"description": "Invalid request (empty message, etc.)"},
        401: {"description": "Authentication required"},
        403: {"description": "Not authorized to access this user's chat"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Server error during AI processing"}
    }
)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Process a chat message and return AI response.

    Flow:
    1. Verify user authorization
    2. Sanitize input message
    3. Load conversation history from database
    4. Process message with Cohere AI agent
    5. Save user message and assistant response to database
    6. Return response with tool actions
    """
    settings = get_settings()

    # Verify user_id matches authenticated user
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's chat"
        )

    # Validate user_id is a valid UUID
    try:
        UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format"
        )

    # Sanitize input message
    sanitizer = InputSanitizer()
    sanitized_message = sanitizer.sanitize(request.message)

    if not sanitized_message or not sanitized_message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty after sanitization"
        )

    # Initialize services
    conversation_service = ConversationService(db)

    # Initialize agent (works with or without API key - demo mode)
    agent = get_agent()
    demo_mode = agent.is_demo_mode

    try:
        # Get or create conversation
        conversation = await conversation_service.get_or_create_conversation(user_id)
        conversation_id = str(conversation.id)

        # Load conversation history
        history = await conversation_service.get_history(conversation_id)

        # Initialize agent with database
        await agent.initialize(database_url=settings.database_url)

        try:
            # Process message with agent
            result: AgentResult = await agent.chat(
                user_id=user_id,
                message=sanitized_message,
                history=history
            )

            # Save user message to database
            await conversation_service.save_user_message(
                conversation_id=conversation_id,
                content=sanitized_message
            )

            # Save assistant response to database
            await conversation_service.save_assistant_message(
                conversation_id=conversation_id,
                content=result.response,
                tool_calls=result.tool_calls if result.tool_calls else None,
                tool_results=None
            )

            # Build response
            actions = [
                ActionTaken(tool=tc["tool"], result=tc.get("result", {}))
                for tc in result.tool_calls
            ] if result.tool_calls else []

            return ChatResponse(
                response=result.response,
                actions_taken=actions,
                conversation_id=conversation_id,
                demo_mode=demo_mode
            )

        finally:
            await agent.cleanup()

    except HTTPException:
        raise
    except Exception as e:
        # Log error
        error_msg = str(e).lower()
        print(f"Chat error: {str(e)}")

        # Handle rate limit errors gracefully
        if "rate" in error_msg or "429" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI service is temporarily unavailable due to rate limits. Please try again in a moment."
            )

        # Handle timeout errors
        if "timeout" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="AI service is taking too long to respond. Please try again."
            )

        # Generic error with friendly message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again."
        )


@router.get(
    "/api/{user_id}/chat/history",
    summary="Get Chat History",
    description="Retrieve conversation history for a user.",
    responses={
        200: {"description": "Conversation history"},
        401: {"description": "Authentication required"},
        403: {"description": "Not authorized"}
    }
)
async def get_chat_history(
    user_id: str,
    limit: int = 50,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get conversation history for a user."""
    # Verify authorization
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's chat history"
        )

    conversation_service = ConversationService(db)

    # Get or create conversation
    conversation = await conversation_service.get_or_create_conversation(user_id)

    # Load history
    history = await conversation_service.get_history(str(conversation.id), limit=limit)

    return {
        "conversation_id": str(conversation.id),
        "messages": history,
        "count": len(history)
    }


@router.delete(
    "/api/{user_id}/chat/history",
    summary="Clear Chat History",
    description="Clear all conversation history for a user.",
    responses={
        200: {"description": "History cleared"},
        401: {"description": "Authentication required"},
        403: {"description": "Not authorized"}
    }
)
async def clear_chat_history(
    user_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Clear conversation history for a user."""
    # Verify authorization
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to clear this user's chat history"
        )

    conversation_service = ConversationService(db)

    # Get conversation
    conversation = await conversation_service.get_or_create_conversation(user_id)

    # Clear history
    success = await conversation_service.clear_conversation(
        str(conversation.id),
        user_id
    )

    if success:
        return {"message": "Chat history cleared", "cleared": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )
