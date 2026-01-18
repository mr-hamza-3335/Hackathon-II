"""
AI Assistant routes.

Provides the /api/v1/ai/chat endpoint for natural language task management.
All requests require authentication via HTTP-only cookie.

SECURITY:
- API key loaded from environment variable only
- Input sanitization and length limits enforced
- No raw model output exposed to client

Requirements: P3-T07, FR-301, FR-302, FR-303, NFR-301, NFR-302, SEC-301
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..config import get_settings
from ..middleware.auth import get_current_user
from ..models import User
from ..ai import AIRequest, AIResponse, IntentRouter, AIClient
from ..ai.client import get_demo_response
from ..ai.errors import (
    AIError,
    InputValidationError,
    AITimeoutError,
    AIRateLimitError,
    map_exception_to_response,
    ERROR_RESPONSES,
)
from ..ai.sanitizer import get_sanitizer

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class ConversationState:
    """
    Simple in-memory conversation state for delete confirmations.

    Note: In production, this should use Redis or similar for
    multi-instance support. For Phase 3, in-memory is acceptable.
    """
    _pending_confirmations: dict[str, dict] = {}

    @classmethod
    def set_pending(cls, user_id: str, confirmation: dict) -> None:
        """Store a pending confirmation for a user."""
        cls._pending_confirmations[user_id] = confirmation

    @classmethod
    def get_pending(cls, user_id: str) -> Optional[dict]:
        """Get pending confirmation for a user."""
        return cls._pending_confirmations.get(user_id)

    @classmethod
    def clear_pending(cls, user_id: str) -> None:
        """Clear pending confirmation for a user."""
        cls._pending_confirmations.pop(user_id, None)


def is_ai_configured() -> bool:
    """
    Check if AI service is properly configured.

    SECURITY: Only checks if env var is set and not a placeholder.
    API key is NEVER logged or exposed.
    """
    key = settings.cohere_api_key
    # Check key exists and is not a placeholder value
    return bool(
        key
        and len(key) > 10
        and key != "your-cohere-api-key"
        and not key.startswith("your-")
    )


def validate_input(message: str) -> str:
    """
    Validate and sanitize user input.

    SECURITY: Enforces max length and basic sanitization.
    """
    if not message or not message.strip():
        raise InputValidationError("Message cannot be empty")

    # Enforce max length
    if len(message) > settings.ai_max_input_length:
        raise InputValidationError(
            f"Message too long. Maximum {settings.ai_max_input_length} characters allowed."
        )

    # Basic sanitization - remove control characters
    sanitized = ''.join(char for char in message if ord(char) >= 32 or char in '\n\r\t')

    return sanitized.strip()


@router.get("/status")
async def ai_status(
    current_user: User = Depends(get_current_user),
):
    """
    Check AI assistant availability.

    Returns status in the exact format required:
    {
        provider: "cohere" | "demo",
        demo_mode: boolean,
        configured: boolean
    }
    """
    configured = is_ai_configured()

    return {
        "provider": "cohere" if configured else "demo",
        "demo_mode": not configured,
        "configured": configured,
        "message": (
            "AI assistant is ready (powered by Cohere)"
            if configured
            else "Demo mode active. Set COHERE_API_KEY environment variable for full AI features."
        ),
    }


@router.post("/chat", response_model=AIResponse)
async def chat(
    request: AIRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a natural language message and return AI response.

    Supported intents: ADD, LIST, COMPLETE, DELETE, HELP

    SECURITY:
    - Input validated and sanitized
    - Max input length enforced
    - No raw model output exposed
    - API key never logged or exposed

    When AI is not configured, returns demo mode responses that still work.
    """
    user_id = str(current_user.id)

    # SECURITY: Validate and sanitize input
    try:
        sanitized_message = validate_input(request.message)
    except InputValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": e.message,
                    "details": [],
                }
            },
        )

    # Check if AI is configured - if not, use demo mode
    if not is_ai_configured():
        logger.info(f"Demo mode active for user {user_id}")
        # Return demo mode response that still provides basic functionality
        demo_response = get_demo_response(sanitized_message)

        # If demo response has an API call action, execute it
        if demo_response.action.type.value == "api_call":
            try:
                # Create intent router for demo execution
                router_instance = IntentRouter(
                    ai_client=None,  # No AI client in demo mode
                    db=db,
                    user_id=current_user.id,
                )

                # Execute the action if it's a valid task operation
                result = await router_instance.execute_action(demo_response)
                await db.commit()
                return result
            except Exception as e:
                logger.warning(f"Demo mode execution failed: {e}")
                await db.rollback()

        return demo_response

    try:
        # Get any pending confirmation for this user
        pending_confirmation = ConversationState.get_pending(user_id)

        # Create the AI client (using Cohere)
        # SECURITY: API key passed from env-loaded config, never hardcoded
        ai_client = AIClient(
            api_key=settings.cohere_api_key,
            model=settings.ai_model,
            timeout=settings.ai_timeout_seconds,
        )

        # Create intent router
        router_instance = IntentRouter(
            ai_client=ai_client,
            db=db,
            user_id=current_user.id,
        )

        # Process the message
        response = await router_instance.process_message(
            message=sanitized_message,
            pending_confirmation=pending_confirmation,
        )

        # Handle pending confirmation state
        if response.data and response.data.get("pending_action"):
            # Store the pending confirmation
            ConversationState.set_pending(user_id, response.data)
        else:
            # Clear any pending confirmation after successful processing
            ConversationState.clear_pending(user_id)

        # Commit database changes
        await db.commit()

        return response

    except InputValidationError as e:
        logger.warning(f"Input validation failed for user {user_id}: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": e.message,
                    "details": [],
                }
            },
        )

    except AITimeoutError:
        logger.warning(f"AI timeout for user {user_id}")
        # Return a graceful fallback response instead of error
        return AIResponse(
            intent="INFO",
            message="The AI is taking longer than expected. Please try again or use demo mode commands like 'show my tasks' or 'add task [name]'.",
            action={"type": "none"},
            data=None
        )

    except AIRateLimitError:
        logger.warning(f"AI rate limited for user {user_id}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "Too many requests. Please wait a moment before trying again.",
                    "details": [],
                }
            },
        )

    except AIError as e:
        logger.error(f"AI error for user {user_id}: {e.message}")
        # SECURITY: Don't expose raw error details to client
        return AIResponse(
            intent="ERROR",
            message="I encountered an issue processing your request. Please try again.",
            action={"type": "none"},
            data=None
        )

    except Exception as e:
        logger.exception(f"Unexpected error in AI chat for user {user_id}")
        await db.rollback()
        # SECURITY: Don't expose internal error details
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again.",
                    "details": [],
                }
            },
        )
