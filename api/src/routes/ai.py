"""
AI Assistant routes.

Provides the /api/v1/ai/chat endpoint for natural language task management.
All requests require authentication via HTTP-only cookie.

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


@router.post("/chat", response_model=AIResponse)
async def chat(
    request: AIRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a natural language message and return AI response.

    FR-301: Accept natural language input for task management
    FR-302: Process through AI model with task context
    FR-303: Return structured response with intent and action
    NFR-301: Respond within 3 seconds (10s timeout on API)
    SEC-301: Require authentication for all AI endpoints
    """
    # Check if AI is configured
    if not settings.anthropic_api_key:
        logger.error("Anthropic API key not configured")
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "AI assistant is not configured. Please set ANTHROPIC_API_KEY.",
                    "details": [],
                }
            },
        )

    user_id = str(current_user.id)

    try:
        # Get any pending confirmation for this user
        pending_confirmation = ConversationState.get_pending(user_id)

        # Create the AI client
        ai_client = AIClient(
            api_key=settings.anthropic_api_key,
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
            message=request.message,
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
        # Return a graceful timeout response instead of error
        return ERROR_RESPONSES["service_unavailable"]

    except AIRateLimitError:
        logger.warning(f"AI rate limited for user {user_id}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "Too many requests. Please wait a moment.",
                    "details": [],
                }
            },
        )

    except AIError as e:
        logger.error(f"AI error for user {user_id}: {e.message}")
        return map_exception_to_response(e)

    except Exception as e:
        logger.exception(f"Unexpected error in AI chat for user {user_id}: {e}")
        await db.rollback()
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


@router.get("/status")
async def ai_status(
    current_user: User = Depends(get_current_user),
):
    """
    Check AI assistant availability.

    Returns whether the AI service is configured and available.
    """
    is_configured = bool(settings.anthropic_api_key)

    return {
        "available": is_configured,
        "model": settings.ai_model if is_configured else None,
        "message": "AI assistant is ready" if is_configured else "AI assistant is not configured",
    }
