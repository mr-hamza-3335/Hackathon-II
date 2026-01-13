"""
AI Assistant input sanitization and security.

Provides input validation, injection pattern detection, and output escaping
to protect against malicious inputs.

Requirements: SEC-309, SEC-310, SEC-311, SEC-312
"""

import re
import html
from typing import Optional
from .errors import InputValidationError


class InputSanitizer:
    """
    Input sanitization and security validation.

    SEC-309: Sanitize all user input before processing
    SEC-310: Reject inputs containing injection patterns
    SEC-311: Enforce input length limits
    SEC-312: Escape special characters in output
    """

    # Maximum allowed lengths
    MAX_MESSAGE_LENGTH = 10000
    MAX_TASK_TITLE_LENGTH = 500

    # Injection patterns to detect and reject
    INJECTION_PATTERNS = [
        # SQL injection patterns
        r"(?i)\b(select|insert|update|delete|drop|truncate|alter|create|union)\b.*\b(from|into|table|database|where)\b",
        r"(?i)(--|;|\/\*|\*\/)",
        r"(?i)\bor\b.*=.*\bor\b",
        r"(?i)\band\b.*=.*\band\b",
        r"'.*(\bor\b|\band\b).*'",

        # XSS patterns
        r"(?i)<\s*script",
        r"(?i)javascript\s*:",
        r"(?i)on\w+\s*=",
        r"(?i)<\s*iframe",
        r"(?i)<\s*object",
        r"(?i)<\s*embed",

        # Shell injection patterns
        r"(?i)(;|\||&|`|\$\(|\$\{)",
        r"(?i)\b(rm|wget|curl|bash|sh|exec|eval)\b.*(-rf|http|>|<|\|)",

        # Path traversal
        r"\.\./",
        r"\.\.\\",
    ]

    # Control characters to strip (except common whitespace)
    CONTROL_CHAR_PATTERN = r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"

    def __init__(self):
        """Initialize the sanitizer with compiled regex patterns."""
        self._injection_patterns = [
            re.compile(pattern) for pattern in self.INJECTION_PATTERNS
        ]
        self._control_char_pattern = re.compile(self.CONTROL_CHAR_PATTERN)

    def sanitize(self, message: str) -> str:
        """
        Sanitize user input message.

        Args:
            message: Raw user input

        Returns:
            Sanitized message

        Raises:
            InputValidationError: If message fails validation
        """
        if not message:
            raise InputValidationError("Message cannot be empty", field="message")

        # Strip control characters
        sanitized = self._control_char_pattern.sub("", message)

        # Normalize whitespace
        sanitized = " ".join(sanitized.split())

        # Check length
        if len(sanitized) > self.MAX_MESSAGE_LENGTH:
            raise InputValidationError(
                f"Message is too long. Maximum {self.MAX_MESSAGE_LENGTH} characters allowed.",
                field="message"
            )

        # Check for injection patterns
        if self.check_injection_patterns(sanitized):
            raise InputValidationError(
                "Your message contains patterns I can't process safely. Please rephrase.",
                field="message"
            )

        return sanitized

    def sanitize_task_title(self, title: str) -> str:
        """
        Sanitize task title input.

        Args:
            title: Raw task title

        Returns:
            Sanitized title

        Raises:
            InputValidationError: If title fails validation
        """
        if not title:
            raise InputValidationError("Task title cannot be empty", field="title")

        # Strip control characters and normalize whitespace
        sanitized = self._control_char_pattern.sub("", title)
        sanitized = " ".join(sanitized.split())

        if not sanitized:
            raise InputValidationError("Task title cannot be empty", field="title")

        # Check length (SEC-311: 500 chars per Phase II spec)
        if len(sanitized) > self.MAX_TASK_TITLE_LENGTH:
            raise InputValidationError(
                f"Task title is too long. Maximum {self.MAX_TASK_TITLE_LENGTH} characters allowed.",
                field="title"
            )

        return sanitized

    def check_injection_patterns(self, text: str) -> bool:
        """
        Check if text contains injection patterns.

        Args:
            text: Text to check

        Returns:
            True if injection pattern detected, False otherwise
        """
        for pattern in self._injection_patterns:
            if pattern.search(text):
                return True
        return False

    def validate_length(self, text: str, max_length: int) -> bool:
        """
        Validate text length.

        Args:
            text: Text to validate
            max_length: Maximum allowed length

        Returns:
            True if valid, False if too long
        """
        return len(text) <= max_length

    @staticmethod
    def escape_output(text: str) -> str:
        """
        Escape special characters in output for safe display.

        SEC-312: Escape special characters in output

        Args:
            text: Text to escape

        Returns:
            HTML-escaped text
        """
        return html.escape(text)

    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """
        Validate UUID format.

        Args:
            uuid_str: String to validate as UUID

        Returns:
            True if valid UUID format, False otherwise
        """
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(uuid_str))


# Singleton instance for convenience
_sanitizer: Optional[InputSanitizer] = None


def get_sanitizer() -> InputSanitizer:
    """Get or create the singleton sanitizer instance."""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = InputSanitizer()
    return _sanitizer
