"""
AI Model API Client.

Handles communication with the AI model service (Cohere).
Implements timeout handling, error recovery, and response parsing.

Requirements: P3-T04, NFR-301
"""

import json
import logging
from typing import Any, Optional

import httpx

from .schemas import AIResponse, Intent, AIAction, ActionType
from .errors import (
    AIModelError,
    AITimeoutError,
    AIRateLimitError,
    AIParseError,
    create_error_response,
)
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class AIClient:
    """
    Client for interacting with the AI model API.

    Handles API communication, response parsing, and error handling.
    Uses Cohere API for natural language processing (FREE tier).
    """

    COHERE_API_URL = "https://api.cohere.com/v2/chat"
    DEFAULT_MODEL = "command-r"  # Free tier model
    DEFAULT_TIMEOUT = 10  # seconds (as per requirements)
    MAX_TOKENS = 1024

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize the AI client.

        Args:
            api_key: Cohere API key
            model: Model identifier (default: command-r)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    async def chat(
        self,
        user_message: str,
        current_tasks: list[dict[str, Any]],
        pending_confirmation: Optional[dict[str, Any]] = None
    ) -> AIResponse:
        """
        Send a message to the AI model and get a structured response.

        Args:
            user_message: The user's natural language input
            current_tasks: List of user's current tasks for context
            pending_confirmation: Any pending action awaiting confirmation

        Returns:
            AIResponse with parsed intent and action

        Raises:
            AITimeoutError: If request times out
            AIRateLimitError: If rate limited by API
            AIModelError: For other API errors
            AIParseError: If response cannot be parsed
        """
        # Build the user prompt with context
        user_prompt = build_user_prompt(
            user_input=user_message,
            current_tasks=current_tasks,
            pending_confirmation=pending_confirmation
        )

        # Prepare the API request for Cohere v2
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Cohere v2 chat format
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "max_tokens": self.MAX_TOKENS,
            "temperature": 0.3,  # Lower temperature for more consistent JSON output
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.COHERE_API_URL,
                    headers=headers,
                    json=payload
                )

                # Handle API errors
                if response.status_code == 429:
                    logger.warning("AI API rate limited")
                    raise AIRateLimitError()

                if response.status_code >= 500:
                    logger.error(f"AI API server error: {response.status_code}")
                    raise AIModelError("AI service is temporarily unavailable")

                if response.status_code >= 400:
                    error_detail = response.text
                    logger.error(f"AI API client error: {response.status_code} - {error_detail}")
                    raise AIModelError("Failed to communicate with AI service")

                # Parse the response
                response_data = response.json()
                return self._parse_response(response_data)

        except httpx.TimeoutException:
            logger.warning("AI API request timed out")
            raise AITimeoutError()

        except httpx.RequestError as e:
            logger.error(f"AI API request failed: {e}")
            raise AIModelError("Failed to connect to AI service")

    def _parse_response(self, response_data: dict[str, Any]) -> AIResponse:
        """
        Parse the AI model response into an AIResponse object.

        Args:
            response_data: Raw API response

        Returns:
            Parsed AIResponse

        Raises:
            AIParseError: If response cannot be parsed
        """
        try:
            # Extract the text content from Cohere's v2 response
            # Response structure: {"message": {"role": "assistant", "content": [{"type": "text", "text": "..."}]}}
            message = response_data.get("message", {})
            content = message.get("content", [])

            if not content:
                raise AIParseError("Empty response from AI model")

            text_content = ""
            for block in content:
                if block.get("type") == "text":
                    text_content = block.get("text", "")
                    break

            if not text_content:
                raise AIParseError("No text content in AI response")

            # Parse the JSON response
            # Clean up the response (remove any markdown formatting)
            clean_text = text_content.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            # Try to find JSON in the response
            if not clean_text.startswith("{"):
                # Try to extract JSON from the text
                start_idx = clean_text.find("{")
                end_idx = clean_text.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    clean_text = clean_text[start_idx:end_idx]
                else:
                    raise AIParseError("Could not find JSON in AI response")

            parsed = json.loads(clean_text)

            # Validate and construct AIResponse
            intent_str = parsed.get("intent", "ERROR").upper()
            try:
                intent = Intent(intent_str)
            except ValueError:
                intent = Intent.ERROR

            message = parsed.get("message", "I encountered an issue processing your request.")

            # Parse action
            action_data = parsed.get("action", {})
            action = AIAction(
                type=ActionType(action_data.get("type", "none")),
                endpoint=action_data.get("endpoint"),
                method=action_data.get("method"),
                payload=action_data.get("payload")
            )

            # Get data
            data = parsed.get("data")

            return AIResponse(
                intent=intent,
                message=message,
                action=action,
                data=data
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}")
            logger.debug(f"Raw response: {response_data}")
            raise AIParseError("Could not parse AI response")

        except Exception as e:
            logger.error(f"Unexpected error parsing AI response: {e}")
            raise AIParseError("Failed to process AI response")


# Fallback responses for when AI is unavailable
def get_fallback_response(user_message: str) -> AIResponse:
    """
    Generate a simple fallback response when AI service is unavailable.

    This provides basic functionality without the AI model.
    """
    message_lower = user_message.lower().strip()

    # Simple keyword matching for basic operations
    if any(word in message_lower for word in ["show", "list", "view", "see", "what"]):
        if "task" in message_lower or "list" in message_lower:
            return AIResponse(
                intent=Intent.LIST,
                message="Here are your tasks.",
                action=AIAction(
                    type=ActionType.API_CALL,
                    endpoint="/tasks",
                    method="GET"
                ),
                data={"filter": "all"}
            )

    if any(word in message_lower for word in ["add", "create", "new"]):
        # Try to extract title
        for prefix in ["add task", "create task", "add a task", "create a task", "new task"]:
            if prefix in message_lower:
                title = message_lower.split(prefix)[-1].strip()
                if title.startswith("to "):
                    title = title[3:]
                if title.startswith(":"):
                    title = title[1:].strip()
                if title:
                    return AIResponse(
                        intent=Intent.CREATE,
                        message=f"I'll create a task '{title}' for you.",
                        action=AIAction(
                            type=ActionType.API_CALL,
                            endpoint="/tasks",
                            method="POST",
                            payload={"title": title}
                        ),
                        data=None
                    )

    if any(word in message_lower for word in ["help", "what can", "how do"]):
        return AIResponse(
            intent=Intent.INFO,
            message="I'm PakAura Assistant. I can help you manage tasks. Try:\n• 'Show my tasks'\n• 'Add task: [description]'\n• 'Complete [task name]'\n• 'Delete [task name]'",
            action=AIAction(type=ActionType.NONE),
            data=None
        )

    # Default clarification
    return AIResponse(
        intent=Intent.CLARIFY,
        message="I'm having trouble understanding. Could you try rephrasing? You can say things like 'Show my tasks' or 'Add task: buy groceries'.",
        action=AIAction(type=ActionType.NONE),
        data=None
    )


# Demo mode responses for when API key is missing
def get_demo_response(user_message: str) -> AIResponse:
    """
    Generate demo mode responses when no API key is configured.

    Provides a friendly experience without requiring a paid API key.
    """
    message_lower = user_message.lower().strip()

    # Demo mode: provide helpful responses based on keywords
    if any(word in message_lower for word in ["show", "list", "view", "see", "all", "my task"]):
        return AIResponse(
            intent=Intent.LIST,
            message="📋 Here are your tasks! (Demo Mode - AI responses are simulated)",
            action=AIAction(
                type=ActionType.API_CALL,
                endpoint="/tasks",
                method="GET"
            ),
            data={"filter": "all"}
        )

    if any(word in message_lower for word in ["add", "create", "new"]):
        # Extract task title from common patterns
        title = None
        for pattern in ["add task ", "create task ", "add a task ", "create a task ", "new task ", "add "]:
            if pattern in message_lower:
                title = message_lower.split(pattern)[-1].strip()
                # Clean up common suffixes
                for suffix in [" to my list", " please", " for me"]:
                    if title.endswith(suffix):
                        title = title[:-len(suffix)]
                break

        if title and len(title) > 0:
            return AIResponse(
                intent=Intent.CREATE,
                message=f"✅ I'll create a task '{title}' for you! (Demo Mode)",
                action=AIAction(
                    type=ActionType.API_CALL,
                    endpoint="/tasks",
                    method="POST",
                    payload={"title": title.title()}
                ),
                data=None
            )

    if any(word in message_lower for word in ["complete", "done", "finish", "mark"]):
        return AIResponse(
            intent=Intent.INFO,
            message="✨ To complete a task in Demo Mode, please use the checkboxes in your task list. Enable AI with a Cohere API key for voice commands!",
            action=AIAction(type=ActionType.NONE),
            data=None
        )

    if any(word in message_lower for word in ["delete", "remove"]):
        return AIResponse(
            intent=Intent.INFO,
            message="🗑️ To delete a task in Demo Mode, please use the task options in your task list. Enable AI with a Cohere API key for voice commands!",
            action=AIAction(type=ActionType.NONE),
            data=None
        )

    if any(word in message_lower for word in ["help", "what can", "how do", "hello", "hi"]):
        return AIResponse(
            intent=Intent.INFO,
            message="👋 Hi! I'm PakAura Assistant running in Demo Mode.\n\n🎯 What I can do:\n• 'Show my tasks' - List all your tasks\n• 'Add task: [name]' - Create a new task\n\n💡 For full AI capabilities (complete, update, delete by voice), add your free Cohere API key!",
            action=AIAction(type=ActionType.NONE),
            data=None
        )

    # Default demo response
    return AIResponse(
        intent=Intent.INFO,
        message="🤖 Demo Mode Active! Try saying:\n• 'Show my tasks'\n• 'Add task buy groceries'\n• 'Help'\n\nFor full AI features, configure your free Cohere API key.",
        action=AIAction(type=ActionType.NONE),
        data=None
    )
