"""
AI Intent Router.

Routes AI responses to appropriate handlers and manages conversation flow.
Handles confirmation states and action execution.

Requirements: P3-T05, FR-306, FR-313, FR-314, FR-315, FR-316
"""

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import AIResponse, AIAction, ActionType, Intent
from .client import AIClient, get_fallback_response
from .task_executor import TaskExecutor
from .sanitizer import InputSanitizer, get_sanitizer
from .errors import (
    AIError,
    AITimeoutError,
    AIRateLimitError,
    AIParseError,
    InputValidationError,
    map_exception_to_response,
    ERROR_RESPONSES,
)

logger = logging.getLogger(__name__)


class IntentRouter:
    """
    Routes AI intents to handlers and manages conversation state.

    FR-306: Parse and classify user intents
    FR-313: Route intents to appropriate handlers
    FR-314: Handle confirmation workflows
    FR-315: Execute task operations
    FR-316: Format responses for frontend
    """

    # Intents that require task execution
    EXECUTABLE_INTENTS = {
        Intent.CREATE,
        Intent.LIST,
        Intent.COMPLETE,
        Intent.UNCOMPLETE,
        Intent.UPDATE,
        Intent.DELETE,
    }

    # Intents that are informational only (no DB operations)
    INFORMATIONAL_INTENTS = {
        Intent.CLARIFY,
        Intent.ERROR,
        Intent.INFO,
    }

    def __init__(
        self,
        ai_client: AIClient,
        db: AsyncSession,
        user_id: UUID
    ):
        """
        Initialize the intent router.

        Args:
            ai_client: The AI client for model communication
            db: Database session for task operations
            user_id: Authenticated user's ID
        """
        self.ai_client = ai_client
        self.db = db
        self.user_id = user_id
        self.task_executor = TaskExecutor(db, user_id)
        self.sanitizer = get_sanitizer()

    async def process_message(
        self,
        message: str,
        pending_confirmation: Optional[dict[str, Any]] = None
    ) -> AIResponse:
        """
        Process a user message and return an AI response.

        This is the main entry point for AI interactions.

        Args:
            message: The user's natural language message
            pending_confirmation: Any pending action awaiting confirmation

        Returns:
            AIResponse with the result of processing
        """
        try:
            # Step 1: Sanitize input
            sanitized_message = self.sanitizer.sanitize(message)

            # Step 2: Get current tasks for context
            current_tasks = await self.task_executor.get_current_tasks()

            # Step 3: Handle confirmation responses
            if pending_confirmation:
                response = await self._handle_confirmation(
                    sanitized_message,
                    pending_confirmation,
                    current_tasks
                )
                if response:
                    return response

            # Step 4: Get AI response
            ai_response = await self._get_ai_response(
                sanitized_message,
                current_tasks,
                pending_confirmation
            )

            # Step 5: Route based on intent
            return await self._route_intent(ai_response)

        except InputValidationError as e:
            logger.warning(f"Input validation failed: {e.message}")
            return ERROR_RESPONSES["injection_detected"]

        except AITimeoutError:
            logger.warning("AI request timed out, using fallback")
            return self._handle_timeout_fallback(message)

        except AIRateLimitError:
            logger.warning("AI rate limited")
            return ERROR_RESPONSES["rate_limited"]

        except AIParseError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return ERROR_RESPONSES["invalid_input"]

        except AIError as e:
            logger.error(f"AI error: {e}")
            return map_exception_to_response(e)

        except Exception as e:
            logger.exception(f"Unexpected error in intent router: {e}")
            return map_exception_to_response(e)

    async def _get_ai_response(
        self,
        message: str,
        current_tasks: list[dict[str, Any]],
        pending_confirmation: Optional[dict[str, Any]]
    ) -> AIResponse:
        """
        Get response from AI model with fallback.

        Args:
            message: Sanitized user message
            current_tasks: User's current tasks for context
            pending_confirmation: Any pending confirmation state

        Returns:
            AIResponse from the model or fallback
        """
        try:
            return await self.ai_client.chat(
                user_message=message,
                current_tasks=current_tasks,
                pending_confirmation=pending_confirmation
            )
        except (AITimeoutError, AIRateLimitError):
            # Re-raise these for specific handling
            raise
        except AIError:
            # Use fallback for other AI errors
            logger.info("Using fallback response due to AI error")
            return get_fallback_response(message)

    async def _route_intent(self, ai_response: AIResponse) -> AIResponse:
        """
        Route the AI response based on intent.

        Args:
            ai_response: The parsed AI response

        Returns:
            Final AIResponse after routing/execution
        """
        intent = ai_response.intent

        # Informational intents don't need execution
        if intent in self.INFORMATIONAL_INTENTS:
            return ai_response

        # Check if this is a delete that needs confirmation
        if intent == Intent.DELETE and not self._is_confirmed_delete(ai_response):
            # AI should have already set up the confirmation prompt
            return ai_response

        # Execute task operations
        if intent in self.EXECUTABLE_INTENTS:
            return await self.task_executor.execute(
                intent=intent,
                action=ai_response.action,
                data=ai_response.data
            )

        # Unknown intent - return as-is
        logger.warning(f"Unhandled intent: {intent}")
        return ai_response

    async def _handle_confirmation(
        self,
        message: str,
        pending_confirmation: dict[str, Any],
        current_tasks: list[dict[str, Any]]
    ) -> Optional[AIResponse]:
        """
        Handle user confirmation for pending actions.

        FR-314: Handle confirmation workflows

        Args:
            message: User's response message
            pending_confirmation: The pending action details
            current_tasks: Current tasks for context

        Returns:
            AIResponse if confirmation handled, None to continue normal processing
        """
        message_lower = message.lower().strip()
        pending_action = pending_confirmation.get("pending_action")
        task_id = pending_confirmation.get("task_id")

        # Check for affirmative response
        if self._is_affirmative(message_lower):
            if pending_action == "DELETE" and task_id:
                # Execute the confirmed delete
                return await self.task_executor.execute(
                    intent=Intent.DELETE,
                    action=AIAction(type=ActionType.API_CALL),
                    data={"task_id": task_id}
                )

        # Check for negative response
        if self._is_negative(message_lower):
            return AIResponse(
                intent=Intent.INFO,
                message="Okay, I've cancelled the deletion.",
                action=AIAction(type=ActionType.NONE),
                data=None
            )

        # Not a clear confirmation - let AI handle it
        return None

    def _is_affirmative(self, message: str) -> bool:
        """Check if message is an affirmative confirmation."""
        affirmative_words = {
            "yes", "yeah", "yep", "yup", "sure", "ok", "okay",
            "confirm", "confirmed", "do it", "proceed", "go ahead",
            "delete it", "remove it", "y", "affirmative"
        }
        return message in affirmative_words or any(
            word in message.split() for word in ["yes", "yeah", "sure", "confirm"]
        )

    def _is_negative(self, message: str) -> bool:
        """Check if message is a negative/cancel response."""
        negative_words = {
            "no", "nope", "nah", "cancel", "stop", "don't",
            "abort", "nevermind", "never mind", "n", "negative"
        }
        return message in negative_words or any(
            word in message.split() for word in ["no", "cancel", "stop", "don't"]
        )

    def _is_confirmed_delete(self, ai_response: AIResponse) -> bool:
        """
        Check if this delete action has been confirmed.

        A delete is confirmed if the AI response indicates direct execution,
        not a clarification request.
        """
        # If the AI is asking for confirmation (CLARIFY with pending_action),
        # this is not a confirmed delete
        if ai_response.intent == Intent.CLARIFY:
            return False

        # If intent is DELETE with an API call action, it's confirmed
        if (ai_response.intent == Intent.DELETE and
            ai_response.action.type == ActionType.API_CALL):
            return True

        return False

    def _handle_timeout_fallback(self, original_message: str) -> AIResponse:
        """
        Handle AI timeout with intelligent fallback.

        Args:
            original_message: The original user message

        Returns:
            Fallback AIResponse
        """
        fallback = get_fallback_response(original_message)

        # Add a note about the AI being slow
        if fallback.intent == Intent.CLARIFY:
            fallback.message = (
                "I'm running a bit slow right now. " + fallback.message
            )

        return fallback


async def create_router(
    api_key: str,
    db: AsyncSession,
    user_id: UUID,
    model: Optional[str] = None,
    timeout: Optional[int] = None
) -> IntentRouter:
    """
    Factory function to create an IntentRouter.

    Args:
        api_key: Anthropic API key
        db: Database session
        user_id: User's ID
        model: Optional model override
        timeout: Optional timeout override

    Returns:
        Configured IntentRouter instance
    """
    ai_client = AIClient(
        api_key=api_key,
        model=model,
        timeout=timeout
    )
    return IntentRouter(ai_client, db, user_id)
