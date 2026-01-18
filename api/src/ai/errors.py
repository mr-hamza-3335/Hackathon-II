"""
AI Assistant error handling.

Defines custom exceptions and error response utilities for the AI module.
Ensures user-friendly error messages without exposing internal details.

Requirements: FR-323, FR-324, FR-325, Section 10.1, Section 10.2
"""

from typing import Optional
from .schemas import AIResponse, Intent, AIAction, ActionType


class AIError(Exception):
    """Base exception for AI-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "AI_ERROR",
        recoverable: bool = True,
        suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.recoverable = recoverable
        self.suggestion = suggestion


class AIModelError(AIError):
    """Error from the AI model API."""

    def __init__(self, message: str = "AI service encountered an error"):
        super().__init__(
            message=message,
            error_code="AI_MODEL_ERROR",
            recoverable=True,
            suggestion="Please try again in a moment."
        )


class AITimeoutError(AIError):
    """AI model request timeout."""

    def __init__(self, message: str = "AI service took too long to respond"):
        super().__init__(
            message=message,
            error_code="AI_TIMEOUT",
            recoverable=True,
            suggestion="Please try again with a shorter message."
        )


class AIRateLimitError(AIError):
    """AI model rate limit exceeded."""

    def __init__(self, message: str = "AI service is temporarily busy"):
        super().__init__(
            message=message,
            error_code="AI_RATE_LIMITED",
            recoverable=True,
            suggestion="Please wait a moment and try again."
        )


class AIParseError(AIError):
    """Failed to parse AI response."""

    def __init__(self, message: str = "Could not understand AI response"):
        super().__init__(
            message=message,
            error_code="AI_PARSE_ERROR",
            recoverable=True,
            suggestion="Please rephrase your request."
        )


class InputValidationError(AIError):
    """Input validation failed."""

    def __init__(self, message: str, field: Optional[str] = None):
        suggestion = f"Please check your {field}." if field else "Please check your input."
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            recoverable=True,
            suggestion=suggestion
        )


class TaskNotFoundError(AIError):
    """Referenced task not found."""

    def __init__(self, message: str = "I couldn't find that task"):
        super().__init__(
            message=message,
            error_code="TASK_NOT_FOUND",
            recoverable=True,
            suggestion="Would you like to see your current tasks?"
        )


class AuthorizationError(AIError):
    """User not authorized for action."""

    def __init__(self, message: str = "I can only access your own tasks"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            recoverable=False,
            suggestion=None
        )


def create_error_response(
    message: str,
    error_code: str = "UNKNOWN_ERROR",
    recoverable: bool = True,
    suggestion: Optional[str] = None
) -> AIResponse:
    """
    Create a standardized error response.

    FR-323: Communicate errors in friendly language
    FR-324: Do not expose internal details
    FR-325: Suggest corrective actions when possible
    """
    return AIResponse(
        intent=Intent.ERROR,
        message=message,
        action=AIAction(type=ActionType.NONE),
        data={
            "error_code": error_code,
            "recoverable": recoverable,
            "suggestion": suggestion
        }
    )


def map_exception_to_response(error: Exception) -> AIResponse:
    """
    Map any exception to an appropriate AIResponse.

    Ensures no internal details are exposed in error responses.
    """
    if isinstance(error, AIError):
        return create_error_response(
            message=error.message,
            error_code=error.error_code,
            recoverable=error.recoverable,
            suggestion=error.suggestion
        )

    # Generic error for unexpected exceptions
    return create_error_response(
        message="Something went wrong. Please try again.",
        error_code="INTERNAL_ERROR",
        recoverable=True,
        suggestion="If the problem persists, try refreshing the page."
    )


# Pre-defined error responses for common scenarios
ERROR_RESPONSES = {
    "auth_required": create_error_response(
        message="Your session has expired. Please log in again.",
        error_code="AUTHENTICATION_ERROR",
        recoverable=False,
        suggestion="Click the login button to continue."
    ),
    "rate_limited": create_error_response(
        message="You've made too many requests. Please wait a moment and try again.",
        error_code="RATE_LIMITED",
        recoverable=True,
        suggestion="Wait about 30 seconds before trying again."
    ),
    "service_unavailable": create_error_response(
        message="The AI assistant is temporarily unavailable. You can still manage tasks using the standard interface.",
        error_code="SERVICE_UNAVAILABLE",
        recoverable=True,
        suggestion="Try the regular task manager or wait a moment."
    ),
    "invalid_input": create_error_response(
        message="I couldn't understand your message. Please try rephrasing.",
        error_code="INVALID_INPUT",
        recoverable=True,
        suggestion="Try a simpler request like 'Show my tasks' or 'Add task: example'."
    ),
    "task_not_found": create_error_response(
        message="I couldn't find that task. Would you like to see your current tasks?",
        error_code="TASK_NOT_FOUND",
        recoverable=True,
        suggestion="Say 'Show my tasks' to see what's available."
    ),
    "injection_detected": create_error_response(
        message="Your message contains characters I can't process. Please rephrase without special characters.",
        error_code="INVALID_INPUT",
        recoverable=True,
        suggestion="Try using plain text without code or special symbols."
    ),
}
