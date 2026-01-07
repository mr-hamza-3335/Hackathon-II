"""Display formatting for the Todo CLI application.

This module provides functions for formatting output messages
including task lists, success messages, and error messages.
"""

from typing import List
from ..models.task import Task


class Display:
    """Handles all output formatting for the CLI."""

    # Application banner
    APP_NAME = "Todo Application"
    APP_VERSION = "1.0.0"

    @staticmethod
    def banner() -> str:
        """Get the application startup banner.

        Returns:
            The startup banner string.
        """
        return (
            f"{Display.APP_NAME} v{Display.APP_VERSION}\n"
            "Type 'help' for available commands."
        )

    @staticmethod
    def prompt() -> str:
        """Get the command prompt string.

        Returns:
            The prompt string.
        """
        return "> "

    @staticmethod
    def goodbye() -> str:
        """Get the goodbye message.

        Returns:
            The goodbye message string.
        """
        return "Goodbye!"

    # Success messages

    @staticmethod
    def task_added(task: Task) -> str:
        """Format the task added confirmation.

        Args:
            task: The newly created task.

        Returns:
            Formatted success message.
        """
        return f"Task added: [{task.id}] {task.title}"

    @staticmethod
    def task_updated(task: Task) -> str:
        """Format the task updated confirmation.

        Args:
            task: The updated task.

        Returns:
            Formatted success message.
        """
        return f"Task [{task.id}] updated: {task.title}"

    @staticmethod
    def task_deleted(task: Task) -> str:
        """Format the task deleted confirmation.

        Args:
            task: The deleted task.

        Returns:
            Formatted success message.
        """
        return f"Task [{task.id}] deleted: {task.title}"

    @staticmethod
    def task_completed(task: Task) -> str:
        """Format the task completed confirmation.

        Args:
            task: The completed task.

        Returns:
            Formatted success message.
        """
        return f"Task [{task.id}] marked as complete: {task.title}"

    @staticmethod
    def task_uncompleted(task: Task) -> str:
        """Format the task uncompleted confirmation.

        Args:
            task: The uncompleted task.

        Returns:
            Formatted success message.
        """
        return f"Task [{task.id}] marked as incomplete: {task.title}"

    @staticmethod
    def task_list(tasks: List[Task]) -> str:
        """Format the task list display.

        Args:
            tasks: List of tasks to display.

        Returns:
            Formatted task list or empty message.
        """
        if not tasks:
            return "No tasks found. Use 'add <title>' to create one."

        lines = ["Tasks:"]
        for task in tasks:
            status = "[x]" if task.completed else "[ ]"
            lines.append(f"[{task.id}] {status} {task.title}")
        return "\n".join(lines)

    # Error messages

    @staticmethod
    def error_task_not_found(task_id: int) -> str:
        """Format the task not found error.

        Args:
            task_id: The ID that was not found.

        Returns:
            Formatted error message.
        """
        return f"Error: Task with ID {task_id} not found"

    @staticmethod
    def error_empty_title() -> str:
        """Format the empty title error.

        Returns:
            Formatted error message.
        """
        return "Error: Task title cannot be empty. Usage: add <title>"

    @staticmethod
    def error_title_too_long() -> str:
        """Format the title too long error.

        Returns:
            Formatted error message.
        """
        return "Error: Task title must be 500 characters or less"

    @staticmethod
    def error_invalid_id() -> str:
        """Format the invalid ID error.

        Returns:
            Formatted error message.
        """
        return "Error: Task ID must be a number"

    @staticmethod
    def error_missing_title() -> str:
        """Format the missing title error for update command.

        Returns:
            Formatted error message.
        """
        return "Error: New title cannot be empty. Usage: update <id> <new_title>"

    @staticmethod
    def error_missing_id(command: str) -> str:
        """Format the missing ID error.

        Args:
            command: The command that needs an ID.

        Returns:
            Formatted error message.
        """
        return f"Error: Missing task ID. Usage: {command} <id>"

    @staticmethod
    def error_missing_arguments() -> str:
        """Format the missing arguments error for update.

        Returns:
            Formatted error message.
        """
        return "Error: Missing arguments. Usage: update <id> <new_title>"

    @staticmethod
    def error_unknown_command(command: str) -> str:
        """Format the unknown command error.

        Args:
            command: The unrecognized command.

        Returns:
            Formatted error message.
        """
        return f"Error: Unknown command '{command}'. Type 'help' for available commands."

    @staticmethod
    def help_text() -> str:
        """Get the help text showing all commands.

        Returns:
            Formatted help text.
        """
        return """Todo Application - Available Commands:

  add <title>           Add a new task
  list                  Show all tasks
  complete <id>         Mark task as complete
  uncomplete <id>       Mark task as incomplete
  update <id> <title>   Update task title
  delete <id>           Delete a task
  help                  Show this help message
  exit                  Exit the application

Examples:
  add Buy groceries
  complete 1
  update 1 Buy groceries from Costco"""
