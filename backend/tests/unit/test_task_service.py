"""Unit tests for the TaskService.

Tests cover all CRUD operations and edge cases.
"""

import pytest
from backend.src.services.task_service import TaskService
from backend.src.models.exceptions import TaskNotFoundError, InvalidTitleError


class TestTaskServiceAdd:
    """Tests for TaskService.add_task (User Story 1)."""

    def test_add_task_creates_task(self):
        """add_task creates a new task with the given title."""
        service = TaskService()
        task = service.add_task("Buy groceries")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.completed is False

    def test_add_task_increments_id(self):
        """Each new task gets a unique incremented ID."""
        service = TaskService()
        task1 = service.add_task("Task 1")
        task2 = service.add_task("Task 2")
        task3 = service.add_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_with_empty_title_raises_error(self):
        """add_task with empty title raises InvalidTitleError."""
        service = TaskService()
        with pytest.raises(InvalidTitleError):
            service.add_task("")

    def test_add_task_with_too_long_title_raises_error(self):
        """add_task with title over 500 chars raises InvalidTitleError."""
        service = TaskService()
        with pytest.raises(InvalidTitleError):
            service.add_task("a" * 501)


class TestTaskServiceList:
    """Tests for TaskService.list_tasks (User Story 2)."""

    def test_list_tasks_empty(self):
        """list_tasks returns empty list when no tasks exist."""
        service = TaskService()
        tasks = service.list_tasks()
        assert tasks == []

    def test_list_tasks_returns_all(self):
        """list_tasks returns all tasks."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")
        service.add_task("Task 3")

        tasks = service.list_tasks()
        assert len(tasks) == 3

    def test_list_tasks_sorted_by_id(self):
        """list_tasks returns tasks sorted by ID."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")
        service.add_task("Task 3")

        tasks = service.list_tasks()
        assert [t.id for t in tasks] == [1, 2, 3]


class TestTaskServiceComplete:
    """Tests for TaskService.complete_task and uncomplete_task (User Story 3)."""

    def test_complete_task(self):
        """complete_task marks the task as complete."""
        service = TaskService()
        service.add_task("Test task")

        task = service.complete_task(1)
        assert task.completed is True

    def test_complete_nonexistent_task_raises_error(self):
        """complete_task with invalid ID raises TaskNotFoundError."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError) as exc_info:
            service.complete_task(999)
        assert exc_info.value.task_id == 999

    def test_uncomplete_task(self):
        """uncomplete_task marks the task as incomplete."""
        service = TaskService()
        service.add_task("Test task")
        service.complete_task(1)

        task = service.uncomplete_task(1)
        assert task.completed is False

    def test_uncomplete_nonexistent_task_raises_error(self):
        """uncomplete_task with invalid ID raises TaskNotFoundError."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError):
            service.uncomplete_task(999)


class TestTaskServiceUpdate:
    """Tests for TaskService.update_task (User Story 4)."""

    def test_update_task(self):
        """update_task changes the task title."""
        service = TaskService()
        service.add_task("Original title")

        task = service.update_task(1, "New title")
        assert task.title == "New title"

    def test_update_nonexistent_task_raises_error(self):
        """update_task with invalid ID raises TaskNotFoundError."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError):
            service.update_task(999, "New title")

    def test_update_task_with_empty_title_raises_error(self):
        """update_task with empty title raises InvalidTitleError."""
        service = TaskService()
        service.add_task("Original title")
        with pytest.raises(InvalidTitleError):
            service.update_task(1, "")

    def test_update_task_with_too_long_title_raises_error(self):
        """update_task with title over 500 chars raises InvalidTitleError."""
        service = TaskService()
        service.add_task("Original title")
        with pytest.raises(InvalidTitleError):
            service.update_task(1, "a" * 501)


class TestTaskServiceDelete:
    """Tests for TaskService.delete_task (User Story 5)."""

    def test_delete_task(self):
        """delete_task removes the task from storage."""
        service = TaskService()
        service.add_task("Task to delete")

        deleted_task = service.delete_task(1)
        assert deleted_task.title == "Task to delete"
        assert service.task_count() == 0

    def test_delete_nonexistent_task_raises_error(self):
        """delete_task with invalid ID raises TaskNotFoundError."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError):
            service.delete_task(999)

    def test_delete_does_not_affect_other_tasks(self):
        """Deleting one task leaves others intact."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")
        service.add_task("Task 3")

        service.delete_task(2)

        tasks = service.list_tasks()
        assert len(tasks) == 2
        assert [t.id for t in tasks] == [1, 3]

    def test_ids_not_reused_after_delete(self):
        """Deleted task IDs are not reused."""
        service = TaskService()
        service.add_task("Task 1")
        service.add_task("Task 2")
        service.delete_task(2)
        task3 = service.add_task("Task 3")

        assert task3.id == 3  # Not 2


class TestTaskServiceGetTask:
    """Tests for TaskService.get_task."""

    def test_get_task(self):
        """get_task returns the correct task."""
        service = TaskService()
        service.add_task("Test task")

        task = service.get_task(1)
        assert task.title == "Test task"

    def test_get_nonexistent_task_raises_error(self):
        """get_task with invalid ID raises TaskNotFoundError."""
        service = TaskService()
        with pytest.raises(TaskNotFoundError):
            service.get_task(999)
