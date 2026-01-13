"""
AI Model API Client.

Handles communication with the AI model service (Anthropic Claude).
Implements timeout handling, error recovery, and response parsing.

Requirements: P3-T04, NFR-301
"""

import json
import asyncio
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
    Uses Anthropic Claude API for natural language processing.
    """

    ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
    DEFAULT_MODEL = "claude-3-haiku-20240307"
    DEFAULT_TIMEOUT = 10  # seconds
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
            api_key: Anthropic API key
            model: Model identifier (default: claude-3-haiku)
            timeout: Request timeout in seconds (default: 10)
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

        # Prepare the API request
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": self.model,
            "max_tokens": self.MAX_TOKENS,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.ANTHROPIC_API_URL,
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
                    logger.error(f"AI API client error: {response.status_code}")
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
            # Extract the text content from Claude's response
            content = response_data.get("content", [])
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
