"""
AI Assistant request/response schemas.

Defines Pydantic models for structured AI communication following
the specification in spec.md Section 7 (AI Prompt Design).

Requirements: FR-307, FR-319, FR-320, FR-321, FR-322
"""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class Intent(str, Enum):
    """
    AI intent classification types.

    Maps user natural language requests to specific task operations.
    """
    CREATE = "CREATE"
    LIST = "LIST"
    COMPLETE = "COMPLETE"
    UNCOMPLETE = "UNCOMPLETE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CLARIFY = "CLARIFY"
    ERROR = "ERROR"
    INFO = "INFO"


class ActionType(str, Enum):
    """Type of action the AI recommends."""
    API_CALL = "api_call"
    NONE = "none"


class AIAction(BaseModel):
    """
    Describes the action to be taken based on AI intent.

    For API_CALL type, includes endpoint details.
    For NONE type, no further action needed.
    """
    type: ActionType = ActionType.NONE
    endpoint: Optional[str] = None
    method: Optional[str] = None
    payload: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


class AIRequest(BaseModel):
    """
    Request schema for AI chat endpoint.

    FR-305: Message contains natural language input
    SEC-311: Message length limited to 10000 characters
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Natural language message from user"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation tracking ID"
    )

    model_config = {"from_attributes": True}


class AIErrorData(BaseModel):
    """
    Additional error information for ERROR intent responses.

    Provides context for error recovery without exposing internals.
    """
    error_code: str = Field(..., description="Error classification code")
    recoverable: bool = Field(
        default=True,
        description="Whether the error can be recovered from"
    )
    suggestion: Optional[str] = Field(
        default=None,
        description="Suggested action for the user"
    )

    model_config = {"from_attributes": True}


class AIResponse(BaseModel):
    """
    Response schema for AI chat endpoint.

    FR-319: Structured JSON response format
    FR-320: Includes operation status via intent
    FR-321: Includes human-readable message
    FR-322: Includes affected task data when applicable
    """
    intent: Intent = Field(..., description="Classified intent type")
    message: str = Field(..., description="Human-readable response message")
    action: AIAction = Field(
        default_factory=lambda: AIAction(type=ActionType.NONE),
        description="Action details if applicable"
    )
    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Task data or additional response data"
    )

    model_config = {"from_attributes": True}

    @classmethod
    def clarify(cls, message: str) -> "AIResponse":
        """Create a clarification response."""
        return cls(
            intent=Intent.CLARIFY,
            message=message,
            action=AIAction(type=ActionType.NONE),
            data=None
        )

    @classmethod
    def error(
        cls,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        recoverable: bool = True,
        suggestion: Optional[str] = None
    ) -> "AIResponse":
        """Create an error response."""
        return cls(
            intent=Intent.ERROR,
            message=message,
            action=AIAction(type=ActionType.NONE),
            data={
                "error_code": error_code,
                "recoverable": recoverable,
                "suggestion": suggestion
            }
        )

    @classmethod
    def info(cls, message: str, data: Optional[dict] = None) -> "AIResponse":
        """Create an informational response."""
        return cls(
            intent=Intent.INFO,
            message=message,
            action=AIAction(type=ActionType.NONE),
            data=data
        )
