"""Command parsing and routing for the Todo CLI application.

This module handles parsing user input, routing to the appropriate
service methods, and returning formatted responses.
"""

from typing import Tuple, Optional
from ..services.task_service import TaskService
from ..models.exceptions import TaskNotFoundError, InvalidTitleError
from .display import Display


class CommandHandler:
    """Handles parsing and execution of CLI commands.

    This class is responsible for:
    - Parsing command strings into command name and arguments
    - Routing commands to the appropriate TaskService methods
    - Handling errors and formatting responses using Display
    """

    def __init__(self, task_service: TaskService):
        """Initialize the command handler.

        Args:
            task_service: The TaskService instance to use for operations.
        """
        self.task_service = task_service
        self.display = Display()

    def execute(self, input_line: str) -> Tuple[str, bool]:
        """Execute a command from user input.

        Args:
            input_line: The raw input string from the user.

        Returns:
            A tuple of (response_message, should_exit).
            should_exit is True only for the 'exit' command.
        """
        # Handle empty input
        if not input_line or not input_line.strip():
            return ("", False)

        # Parse command and arguments
        parts = input_line.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Route to appropriate handler
        handlers = {
            "add": self._handle_add,
            "list": self._handle_list,
            "complete": self._handle_complete,
            "uncomplete": self._handle_uncomplete,
            "update": self._handle_update,
            "delete": self._handle_delete,
            "help": self._handle_help,
            "exit": self._handle_exit,
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return (Display.error_unknown_command(command), False)

    def _handle_add(self, args: str) -> Tuple[str, bool]:
        """Handle the 'add' command.

        Args:
            args: The task title to add.

        Returns:
            Tuple of (response message, should_exit=False).
        """
        if not args or not args.strip():
            return (Display.error_empty_title(), False)

        try:
            task = self.task_service.add_task(args)
            return (Display.task_added(task), False)
        except InvalidTitleError as e:
            if "500 characters" in str(e):
                return (Display.error_title_too_long(), False)
            return (Display.error_empty_title(), False)

    def _handle_list(self, args: str) -> Tuple[str, bool]:
        """Handle the 'list' command.

        Args:
            args: Ignored for list command.

        Returns:
            Tuple of (formatted task list, should_exit=False).
        """
        tasks = self.task_service.list_tasks()
        return (Display.task_list(tasks), False)

    def _handle_complete(self, args: str) -> Tuple[str, bool]:
        """Handle the 'complete' command.

        Args:
            args: The task ID to complete.

        Returns:
            Tuple of (response message, should_exit=False).
        """
        task_id = self._parse_id(args)
        if task_id is None:
            if not args or not args.strip():
                return (Display.error_missing_id("complete"), False)
            return (Display.error_invalid_id(), False)

        try:
            task = self.task_service.complete_task(task_id)
            return (Display.task_completed(task), False)
        except TaskNotFoundError:
            return (Display.error_task_not_found(task_id), False)

    def _handle_uncomplete(self, args: str) -> Tuple[str, bool]:
        """Handle the 'uncomplete' command.

        Args:
            args: The task ID to uncomplete.

        Returns:
            Tuple of (response message, should_exit=False).
        """
        task_id = self._parse_id(args)
        if task_id is None:
            if not args or not args.strip():
                return (Display.error_missing_id("uncomplete"), False)
            return (Display.error_invalid_id(), False)

        try:
            task = self.task_service.uncomplete_task(task_id)
            return (Display.task_uncompleted(task), False)
        except TaskNotFoundError:
            return (Display.error_task_not_found(task_id), False)

    def _handle_update(self, args: str) -> Tuple[str, bool]:
        """Handle the 'update' command.

        Args:
            args: The task ID and new title (space-separated).

        Returns:
            Tuple of (response message, should_exit=False).
        """
        if not args or not args.strip():
            return (Display.error_missing_arguments(), False)

        parts = args.strip().split(maxsplit=1)

        # Parse ID
        task_id = self._parse_id(parts[0])
        if task_id is None:
            return (Display.error_invalid_id(), False)

        # Check for title
        if len(parts) < 2 or not parts[1].strip():
            return (Display.error_missing_title(), False)

        new_title = parts[1]

        try:
            task = self.task_service.update_task(task_id, new_title)
            return (Display.task_updated(task), False)
        except TaskNotFoundError:
            return (Display.error_task_not_found(task_id), False)
        except InvalidTitleError as e:
            if "500 characters" in str(e):
                return (Display.error_title_too_long(), False)
            return (Display.error_missing_title(), False)

    def _handle_delete(self, args: str) -> Tuple[str, bool]:
        """Handle the 'delete' command.

        Args:
            args: The task ID to delete.

        Returns:
            Tuple of (response message, should_exit=False).
        """
        task_id = self._parse_id(args)
        if task_id is None:
            if not args or not args.strip():
                return (Display.error_missing_id("delete"), False)
            return (Display.error_invalid_id(), False)

        try:
            task = self.task_service.delete_task(task_id)
            return (Display.task_deleted(task), False)
        except TaskNotFoundError:
            return (Display.error_task_not_found(task_id), False)

    def _handle_help(self, args: str) -> Tuple[str, bool]:
        """Handle the 'help' command.

        Args:
            args: Ignored for help command.

        Returns:
            Tuple of (help text, should_exit=False).
        """
        return (Display.help_text(), False)

    def _handle_exit(self, args: str) -> Tuple[str, bool]:
        """Handle the 'exit' command.

        Args:
            args: Ignored for exit command.

        Returns:
            Tuple of (goodbye message, should_exit=True).
        """
        return (Display.goodbye(), True)

    @staticmethod
    def _parse_id(value: str) -> Optional[int]:
        """Parse a string value as a task ID.

        Args:
            value: The string to parse.

        Returns:
            The parsed integer ID, or None if parsing fails.
        """
        if not value or not value.strip():
            return None
        try:
            return int(value.strip())
        except ValueError:
            return None
