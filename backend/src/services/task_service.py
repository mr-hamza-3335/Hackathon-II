"""Task service for managing todo tasks.

This module provides the business logic for CRUD operations on tasks.
All tasks are stored in memory and lost when the application exits.
"""

from typing import Dict, List
from ..models.task import Task
from ..models.exceptions import TaskNotFoundError


class TaskService:
    """Service for managing tasks in memory.

    This service maintains an in-memory dictionary of tasks and provides
    methods for creating, reading, updating, and deleting tasks.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects.
        _next_id: Counter for generating unique task IDs.
    """

    def __init__(self):
        """Initialize the task service with empty storage."""
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str) -> Task:
        """Create and store a new task.

        Args:
            title: The title for the new task.

        Returns:
            The newly created Task object.

        Raises:
            InvalidTitleError: If the title is invalid.
        """
        task = Task(self._next_id, title)
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def list_tasks(self) -> List[Task]:
        """Get all tasks sorted by ID.

        Returns:
            List of all tasks, sorted by ID in ascending order.
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def get_task(self, task_id: int) -> Task:
        """Get a task by its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task object with the specified ID.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def update_task(self, task_id: int, new_title: str) -> Task:
        """Update a task's title.

        Args:
            task_id: The ID of the task to update.
            new_title: The new title for the task.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
            InvalidTitleError: If the new title is invalid.
        """
        task = self.get_task(task_id)
        task.update_title(new_title)
        return task

    def delete_task(self, task_id: int) -> Task:
        """Delete a task.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            The deleted Task object (for confirmation message).

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
        """
        task = self.get_task(task_id)
        del self._tasks[task_id]
        return task

    def complete_task(self, task_id: int) -> Task:
        """Mark a task as complete.

        Args:
            task_id: The ID of the task to complete.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
        """
        task = self.get_task(task_id)
        task.mark_complete()
        return task

    def uncomplete_task(self, task_id: int) -> Task:
        """Mark a task as incomplete.

        Args:
            task_id: The ID of the task to mark incomplete.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If no task exists with the given ID.
        """
        task = self.get_task(task_id)
        task.mark_incomplete()
        return task

    def task_count(self) -> int:
        """Get the number of tasks.

        Returns:
            The total number of tasks in storage.
        """
        return len(self._tasks)
