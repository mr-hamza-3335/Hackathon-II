"""
AI Assistant module for PakAura Phase 3.

This module provides natural language task management capabilities
through an AI-powered assistant that interfaces with existing task APIs.
"""

from .schemas import (
    Intent,
    ActionType,
    AIAction,
    AIRequest,
    AIResponse,
    AIErrorData,
)
from .prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    build_user_prompt,
)
from .client import AIClient
from .intent_router import IntentRouter
from .task_executor import TaskExecutor
from .sanitizer import InputSanitizer
from .errors import (
    AIError,
    AIModelError,
    AITimeoutError,
    AIRateLimitError,
    AIParseError,
    create_error_response,
)

__all__ = [
    # Schemas
    "Intent",
    "ActionType",
    "AIAction",
    "AIRequest",
    "AIResponse",
    "AIErrorData",
    # Prompts
    "SYSTEM_PROMPT",
    "USER_PROMPT_TEMPLATE",
    "build_user_prompt",
    # Client
    "AIClient",
    # Router
    "IntentRouter",
    # Executor
    "TaskExecutor",
    # Sanitizer
    "InputSanitizer",
    # Errors
    "AIError",
    "AIModelError",
    "AITimeoutError",
    "AIRateLimitError",
    "AIParseError",
    "create_error_response",
]
