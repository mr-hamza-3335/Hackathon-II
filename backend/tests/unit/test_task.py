"""Unit tests for the Task model.

Tests cover task creation, validation, and state transitions.
"""

import pytest
from backend.src.models.task import Task, MAX_TITLE_LENGTH
from backend.src.models.exceptions import InvalidTitleError


class TestTaskCreation:
    """Tests for Task creation and validation."""

    def test_create_task_with_valid_title(self):
        """Task can be created with a valid title."""
        task = Task(1, "Buy groceries")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.completed is False
        assert task.created_at is not None

    def test_create_task_strips_whitespace(self):
        """Task title is stripped of leading/trailing whitespace."""
        task = Task(1, "  Buy groceries  ")
        assert task.title == "Buy groceries"

    def test_create_task_with_empty_title_raises_error(self):
        """Creating task with empty title raises InvalidTitleError."""
        with pytest.raises(InvalidTitleError) as exc_info:
            Task(1, "")
        assert "cannot be empty" in str(exc_info.value)

    def test_create_task_with_whitespace_only_raises_error(self):
        """Creating task with whitespace-only title raises InvalidTitleError."""
        with pytest.raises(InvalidTitleError) as exc_info:
            Task(1, "   ")
        assert "cannot be empty" in str(exc_info.value)

    def test_create_task_with_max_length_title(self):
        """Task can be created with title at max length."""
        title = "a" * MAX_TITLE_LENGTH
        task = Task(1, title)
        assert len(task.title) == MAX_TITLE_LENGTH

    def test_create_task_with_too_long_title_raises_error(self):
        """Creating task with title over 500 chars raises InvalidTitleError."""
        title = "a" * (MAX_TITLE_LENGTH + 1)
        with pytest.raises(InvalidTitleError) as exc_info:
            Task(1, title)
        assert "500 characters or less" in str(exc_info.value)


class TestTaskStateTransitions:
    """Tests for Task completion state changes."""

    def test_mark_complete(self):
        """Task can be marked as complete."""
        task = Task(1, "Test task")
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_mark_incomplete(self):
        """Completed task can be marked as incomplete."""
        task = Task(1, "Test task")
        task.mark_complete()
        assert task.completed is True
        task.mark_incomplete()
        assert task.completed is False


class TestTaskUpdate:
    """Tests for updating task title."""

    def test_update_title(self):
        """Task title can be updated."""
        task = Task(1, "Original title")
        task.update_title("New title")
        assert task.title == "New title"

    def test_update_title_strips_whitespace(self):
        """Updated title is stripped of whitespace."""
        task = Task(1, "Original title")
        task.update_title("  New title  ")
        assert task.title == "New title"

    def test_update_title_with_empty_raises_error(self):
        """Updating with empty title raises InvalidTitleError."""
        task = Task(1, "Original title")
        with pytest.raises(InvalidTitleError):
            task.update_title("")

    def test_update_title_with_too_long_raises_error(self):
        """Updating with too long title raises InvalidTitleError."""
        task = Task(1, "Original title")
        with pytest.raises(InvalidTitleError):
            task.update_title("a" * (MAX_TITLE_LENGTH + 1))


class TestTaskRepr:
    """Tests for Task string representation."""

    def test_repr_pending_task(self):
        """Pending task repr shows correct status."""
        task = Task(1, "Test task")
        assert "pending" in repr(task)
        assert "Test task" in repr(task)

    def test_repr_completed_task(self):
        """Completed task repr shows correct status."""
        task = Task(1, "Test task")
        task.mark_complete()
        assert "completed" in repr(task)
