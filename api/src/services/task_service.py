"""
Task service for CRUD operations with user isolation.
T052, T057, T065, T072, T077: Task service methods
Requirements: FR-008, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ..models import Task


class AuthorizationError(Exception):
    """Raised when user tries to access another user's task."""
    pass


class NotFoundError(Exception):
    """Raised when task is not found."""
    pass


class TaskService:
    """
    Task management service with user isolation.

    SECURITY: All task queries MUST include user_id filter (FR-008).
    """

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: UUID,
        title: str,
    ) -> Task:
        """
        Create a new task for the user.

        FR-009: Allow authenticated users to create tasks with a title
        FR-010: Auto-generate unique IDs for each task
        FR-016: Validate task titles (1-500 characters, non-empty)
        FR-017: Persist all task data to the database
        FR-018: Associate each task with its owner's user ID
        """
        task = Task(user_id=user_id, title=title.strip(), completed=False)
        db.add(task)
        await db.flush()
        return task

    @staticmethod
    async def list(
        db: AsyncSession,
        user_id: UUID,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """
        List all tasks for a user.

        FR-008: Restrict task access to the task owner only
        FR-011: Allow authenticated users to view their task list
        """
        query = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            query = query.where(Task.completed == completed)

        # Order by created_at descending (newest first)
        query = query.order_by(desc(Task.created_at))

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get(
        db: AsyncSession,
        task_id: UUID,
        user_id: UUID,
    ) -> Task:
        """
        Get a single task by ID with user ownership verification.

        FR-008: Restrict task access to the task owner only
        Raises: NotFoundError if task doesn't exist
        Raises: AuthorizationError if task belongs to another user
        """
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise NotFoundError("Task not found")

        # T087: Authorization check for cross-user access
        if task.user_id != user_id:
            raise AuthorizationError("Access denied")

        return task

    @staticmethod
    async def update(
        db: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> Task:
        """
        Update a task's title and/or completion status.

        FR-014: Allow authenticated users to update task titles
        FR-016: Validate task titles (1-500 characters, non-empty)
        FR-008: Restrict task access to the task owner only
        """
        task = await TaskService.get(db, task_id, user_id)

        if title is not None:
            task.title = title.strip()

        if completed is not None:
            task.completed = completed

        await db.flush()
        return task

    @staticmethod
    async def toggle_complete(
        db: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        completed: bool,
    ) -> Task:
        """
        Toggle task completion status.

        FR-012: Allow authenticated users to mark tasks complete
        FR-013: Allow authenticated users to mark tasks incomplete
        FR-017: Persist all task data to the database
        """
        return await TaskService.update(db, task_id, user_id, completed=completed)

    @staticmethod
    async def delete(
        db: AsyncSession,
        task_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Delete a task permanently.

        FR-015: Allow authenticated users to delete tasks
        FR-008: Restrict task access to the task owner only
        """
        task = await TaskService.get(db, task_id, user_id)
        await db.delete(task)
        await db.flush()
