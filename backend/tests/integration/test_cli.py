"""Integration tests for the CLI commands.

Tests cover the full command flow from input to output.
"""

import pytest
from backend.src.services.task_service import TaskService
from backend.src.cli.commands import CommandHandler


@pytest.fixture
def handler():
    """Create a fresh CommandHandler with empty TaskService."""
    service = TaskService()
    return CommandHandler(service)


class TestAddCommand:
    """Integration tests for the 'add' command (User Story 1)."""

    def test_add_task_success(self, handler):
        """Add command creates task and returns confirmation."""
        response, should_exit = handler.execute("add Buy groceries")

        assert should_exit is False
        assert "Task added:" in response
        assert "[1]" in response
        assert "Buy groceries" in response

    def test_add_task_with_spaces_in_title(self, handler):
        """Add command handles titles with multiple words."""
        response, _ = handler.execute("add Buy groceries from the store")

        assert "Buy groceries from the store" in response

    def test_add_task_empty_title(self, handler):
        """Add command with no title returns error."""
        response, should_exit = handler.execute("add")

        assert should_exit is False
        assert "Error:" in response
        assert "cannot be empty" in response

    def test_add_task_whitespace_only(self, handler):
        """Add command with whitespace-only title returns error."""
        response, _ = handler.execute("add    ")

        assert "Error:" in response
        assert "cannot be empty" in response


class TestListCommand:
    """Integration tests for the 'list' command (User Story 2)."""

    def test_list_empty(self, handler):
        """List command with no tasks shows empty message."""
        response, should_exit = handler.execute("list")

        assert should_exit is False
        assert "No tasks found" in response

    def test_list_with_tasks(self, handler):
        """List command shows all tasks."""
        handler.execute("add Task 1")
        handler.execute("add Task 2")

        response, _ = handler.execute("list")

        assert "Tasks:" in response
        assert "[1]" in response
        assert "Task 1" in response
        assert "[2]" in response
        assert "Task 2" in response

    def test_list_shows_status(self, handler):
        """List command shows completion status."""
        handler.execute("add Incomplete task")
        handler.execute("add Complete task")
        handler.execute("complete 2")

        response, _ = handler.execute("list")

        # Incomplete task should have [ ]
        # Complete task should have [x]
        assert "[ ]" in response
        assert "[x]" in response


class TestCompleteCommand:
    """Integration tests for 'complete' command (User Story 3)."""

    def test_complete_task(self, handler):
        """Complete command marks task as complete."""
        handler.execute("add Test task")

        response, should_exit = handler.execute("complete 1")

        assert should_exit is False
        assert "marked as complete" in response
        assert "[1]" in response

    def test_complete_nonexistent_task(self, handler):
        """Complete command with invalid ID returns error."""
        response, _ = handler.execute("complete 999")

        assert "Error:" in response
        assert "not found" in response

    def test_complete_no_id(self, handler):
        """Complete command with no ID returns error."""
        response, _ = handler.execute("complete")

        assert "Error:" in response
        assert "Missing task ID" in response

    def test_complete_invalid_id(self, handler):
        """Complete command with non-numeric ID returns error."""
        response, _ = handler.execute("complete abc")

        assert "Error:" in response
        assert "must be a number" in response


class TestUncompleteCommand:
    """Integration tests for 'uncomplete' command (User Story 3)."""

    def test_uncomplete_task(self, handler):
        """Uncomplete command marks task as incomplete."""
        handler.execute("add Test task")
        handler.execute("complete 1")

        response, should_exit = handler.execute("uncomplete 1")

        assert should_exit is False
        assert "marked as incomplete" in response

    def test_uncomplete_nonexistent_task(self, handler):
        """Uncomplete command with invalid ID returns error."""
        response, _ = handler.execute("uncomplete 999")

        assert "Error:" in response
        assert "not found" in response


class TestUpdateCommand:
    """Integration tests for 'update' command (User Story 4)."""

    def test_update_task(self, handler):
        """Update command changes task title."""
        handler.execute("add Original title")

        response, should_exit = handler.execute("update 1 New title")

        assert should_exit is False
        assert "updated" in response
        assert "New title" in response

    def test_update_with_spaces_in_title(self, handler):
        """Update command handles multi-word titles."""
        handler.execute("add Original")

        response, _ = handler.execute("update 1 New title with spaces")

        assert "New title with spaces" in response

    def test_update_nonexistent_task(self, handler):
        """Update command with invalid ID returns error."""
        response, _ = handler.execute("update 999 New title")

        assert "Error:" in response
        assert "not found" in response

    def test_update_no_args(self, handler):
        """Update command with no arguments returns error."""
        response, _ = handler.execute("update")

        assert "Error:" in response
        assert "Missing arguments" in response

    def test_update_no_title(self, handler):
        """Update command with ID but no title returns error."""
        handler.execute("add Test task")

        response, _ = handler.execute("update 1")

        assert "Error:" in response
        assert "cannot be empty" in response

    def test_update_invalid_id(self, handler):
        """Update command with non-numeric ID returns error."""
        response, _ = handler.execute("update abc New title")

        assert "Error:" in response
        assert "must be a number" in response


class TestDeleteCommand:
    """Integration tests for 'delete' command (User Story 5)."""

    def test_delete_task(self, handler):
        """Delete command removes task."""
        handler.execute("add Task to delete")

        response, should_exit = handler.execute("delete 1")

        assert should_exit is False
        assert "deleted" in response

        # Verify task is gone
        list_response, _ = handler.execute("list")
        assert "No tasks found" in list_response

    def test_delete_nonexistent_task(self, handler):
        """Delete command with invalid ID returns error."""
        response, _ = handler.execute("delete 999")

        assert "Error:" in response
        assert "not found" in response

    def test_delete_no_id(self, handler):
        """Delete command with no ID returns error."""
        response, _ = handler.execute("delete")

        assert "Error:" in response
        assert "Missing task ID" in response


class TestHelpCommand:
    """Integration tests for 'help' command."""

    def test_help_shows_all_commands(self, handler):
        """Help command shows all available commands."""
        response, should_exit = handler.execute("help")

        assert should_exit is False
        assert "add" in response
        assert "list" in response
        assert "complete" in response
        assert "uncomplete" in response
        assert "update" in response
        assert "delete" in response
        assert "help" in response
        assert "exit" in response


class TestExitCommand:
    """Integration tests for 'exit' command."""

    def test_exit_returns_true(self, handler):
        """Exit command returns should_exit=True."""
        response, should_exit = handler.execute("exit")

        assert should_exit is True
        assert "Goodbye" in response


class TestUnknownCommand:
    """Integration tests for unknown commands."""

    def test_unknown_command(self, handler):
        """Unknown command returns error message."""
        response, should_exit = handler.execute("foo")

        assert should_exit is False
        assert "Error:" in response
        assert "Unknown command" in response
        assert "foo" in response

    def test_empty_input(self, handler):
        """Empty input returns empty response."""
        response, should_exit = handler.execute("")

        assert should_exit is False
        assert response == ""

    def test_whitespace_input(self, handler):
        """Whitespace-only input returns empty response."""
        response, should_exit = handler.execute("   ")

        assert should_exit is False
        assert response == ""


class TestCaseInsensitivity:
    """Tests for command case insensitivity."""

    def test_uppercase_command(self, handler):
        """Commands work with uppercase."""
        response, _ = handler.execute("LIST")
        assert "No tasks found" in response or "Tasks:" in response

    def test_mixed_case_command(self, handler):
        """Commands work with mixed case."""
        response, _ = handler.execute("HeLp")
        assert "Available Commands" in response
