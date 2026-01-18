"""
AI Assistant module for PakAura Phase 3.

This module provides natural language task management capabilities
through an AI-powered assistant that interfaces with existing task APIs.

Phase III: Cohere AI Integration (FREE tier)
- Uses Cohere's command-r model for conversational responses
- Lightweight intent detection with keyword NLP
- DEMO MODE when API key is not configured
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
from .sanitizer import InputSanitizer
from .errors import (
    AIError,
    AIModelError,
    AITimeoutError,
    AIRateLimitError,
    AIParseError,
    create_error_response,
)
from .agent import CohereTaskAgent, TaskManagerAgent, SimplifiedTaskAgent, AgentResult, get_agent

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
    # Sanitizer
    "InputSanitizer",
    # Errors
    "AIError",
    "AIModelError",
    "AITimeoutError",
    "AIRateLimitError",
    "AIParseError",
    "create_error_response",
    # Phase III: Cohere AI Agent
    "CohereTaskAgent",
    "TaskManagerAgent",
    "SimplifiedTaskAgent",
    "AgentResult",
    "get_agent",
]
