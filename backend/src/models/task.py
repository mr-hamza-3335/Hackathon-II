"""Task model for the Todo application.

This module defines the Task entity representing a single todo item.
Tasks have an ID, title, completion status, and creation timestamp.
"""

from datetime import datetime
from .exceptions import InvalidTitleError


# Maximum allowed length for task titles
MAX_TITLE_LENGTH = 500


class Task:
    """Represents a single todo task.

    Attributes:
        id: Unique identifier for the task (auto-generated).
        title: The task description (1-500 characters).
        completed: Whether the task is complete (default: False).
        created_at: When the task was created (auto-generated).
    """

    def __init__(self, task_id: int, title: str):
        """Create a new Task.

        Args:
            task_id: Unique identifier for this task.
            title: The task description (will be validated).

        Raises:
            InvalidTitleError: If title is empty or exceeds 500 characters.
        """
        self._validate_title(title)
        self.id = task_id
        self.title = title.strip()
        self.completed = False
        self.created_at = datetime.now()

    @staticmethod
    def _validate_title(title: str) -> None:
        """Validate that a title meets requirements.

        Args:
            title: The title to validate.

        Raises:
            InvalidTitleError: If title is empty, whitespace-only, or too long.
        """
        if not title or not title.strip():
            raise InvalidTitleError("Task title cannot be empty")
        if len(title.strip()) > MAX_TITLE_LENGTH:
            raise InvalidTitleError(
                f"Task title must be {MAX_TITLE_LENGTH} characters or less"
            )

    def update_title(self, new_title: str) -> None:
        """Update the task title.

        Args:
            new_title: The new title for the task.

        Raises:
            InvalidTitleError: If new_title is empty or exceeds 500 characters.
        """
        self._validate_title(new_title)
        self.title = new_title.strip()

    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as incomplete."""
        self.completed = False

    def __repr__(self) -> str:
        """Return a string representation of the task."""
        status = "completed" if self.completed else "pending"
        return f"Task(id={self.id}, title='{self.title}', status={status})"
