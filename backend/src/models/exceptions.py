"""Custom exceptions for the Todo application.

This module defines the exception hierarchy for handling todo-related errors.
All custom exceptions inherit from TodoError for easy catching.
"""


class TodoError(Exception):
    """Base exception for all todo application errors.

    All custom exceptions in this application inherit from this class,
    allowing callers to catch all todo-related errors with a single except clause.
    """
    pass


class TaskNotFoundError(TodoError):
    """Raised when a task with the specified ID does not exist.

    Attributes:
        task_id: The ID that was not found.
        message: Explanation of the error.
    """

    def __init__(self, task_id: int):
        self.task_id = task_id
        self.message = f"Task with ID {task_id} not found"
        super().__init__(self.message)


class InvalidTitleError(TodoError):
    """Raised when a task title is invalid (empty or too long).

    Attributes:
        reason: Why the title is invalid.
        message: Explanation of the error.
    """

    def __init__(self, reason: str):
        self.reason = reason
        self.message = reason
        super().__init__(self.message)
