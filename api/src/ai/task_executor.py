"""
AI Task Executor.

Executes task operations via the existing TaskService.
Acts as a bridge between AI intents and the task management layer.

Requirements: P3-T06, FR-308, FR-309, FR-310, FR-311, FR-312
"""

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..services.task_service import TaskService, NotFoundError, AuthorizationError
from .schemas import AIResponse, AIAction, ActionType, Intent
from .errors import TaskNotFoundError, AuthorizationError as AIAuthorizationError

logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    Executes task operations based on AI intents.

    FR-308: Map AI intents to task CRUD operations
    FR-309: Execute only authorized operations
    FR-310: Format responses for AI consumption
    """

    def __init__(self, db: AsyncSession, user_id: UUID):
        """
        Initialize the task executor.

        Args:
            db: Database session for task operations
            user_id: Authenticated user's ID for authorization
        """
        self.db = db
        self.user_id = user_id

    async def execute(
        self,
        intent: Intent,
        action: AIAction,
        data: Optional[dict[str, Any]] = None
    ) -> AIResponse:
        """
        Execute the appropriate task operation based on intent.

        Args:
            intent: The classified intent from AI
            action: The action details including endpoint and payload
            data: Additional data (task_id, filter, etc.)

        Returns:
            AIResponse with operation result
        """
        try:
            if intent == Intent.CREATE:
                return await self._create_task(action, data)
            elif intent == Intent.LIST:
                return await self._list_tasks(data)
            elif intent == Intent.COMPLETE:
                return await self._complete_task(data)
            elif intent == Intent.UNCOMPLETE:
                return await self._uncomplete_task(data)
            elif intent == Intent.UPDATE:
                return await self._update_task(action, data)
            elif intent == Intent.DELETE:
                return await self._delete_task(data)
            else:
                # Non-action intents (CLARIFY, ERROR, INFO) don't need execution
                return AIResponse(
                    intent=intent,
                    message="No action required.",
                    action=AIAction(type=ActionType.NONE),
                    data=data
                )

        except NotFoundError:
            raise TaskNotFoundError("I couldn't find that task. Would you like to see your current tasks?")
        except AuthorizationError:
            raise AIAuthorizationError("I can only access your own tasks.")

    async def _create_task(
        self,
        action: AIAction,
        data: Optional[dict[str, Any]]
    ) -> AIResponse:
        """
        Create a new task.

        FR-309: Create task via TaskService
        """
        payload = action.payload or {}
        title = payload.get("title", "").strip()

        if not title:
            return AIResponse(
                intent=Intent.CLARIFY,
                message="What would you like to name the task?",
                action=AIAction(type=ActionType.NONE),
                data=None
            )

        task = await TaskService.create(
            db=self.db,
            user_id=self.user_id,
            title=title
        )

        return AIResponse(
            intent=Intent.CREATE,
            message=f"I've created the task '{task.title}' for you.",
            action=AIAction(type=ActionType.NONE),
            data={
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
            }
        )

    async def _list_tasks(self, data: Optional[dict[str, Any]]) -> AIResponse:
        """
        List user's tasks with optional filter.

        FR-311: Return task list to user
        """
        filter_type = (data or {}).get("filter", "all")

        completed = None
        if filter_type == "completed":
            completed = True
        elif filter_type == "incomplete":
            completed = False

        tasks = await TaskService.list(
            db=self.db,
            user_id=self.user_id,
            completed=completed
        )

        task_list = [
            {
                "id": str(task.id),
                "title": task.title,
                "completed": task.completed,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
            for task in tasks
        ]

        if not tasks:
            if filter_type == "completed":
                message = "You don't have any completed tasks yet."
            elif filter_type == "incomplete":
                message = "You don't have any incomplete tasks. Great job!"
            else:
                message = "You don't have any tasks yet. Would you like to create one?"
        else:
            count = len(tasks)
            if filter_type == "completed":
                message = f"Here are your {count} completed task{'s' if count != 1 else ''}."
            elif filter_type == "incomplete":
                message = f"Here are your {count} incomplete task{'s' if count != 1 else ''}."
            else:
                message = f"Here are your {count} task{'s' if count != 1 else ''}."

        return AIResponse(
            intent=Intent.LIST,
            message=message,
            action=AIAction(type=ActionType.NONE),
            data={"tasks": task_list, "filter": filter_type, "count": len(task_list)}
        )

    async def _complete_task(self, data: Optional[dict[str, Any]]) -> AIResponse:
        """
        Mark a task as complete.

        FR-312: Toggle task completion status
        """
        task_id = self._extract_task_id(data)
        if not task_id:
            return AIResponse(
                intent=Intent.CLARIFY,
                message="Which task would you like to complete? Please provide the task name or ID.",
                action=AIAction(type=ActionType.NONE),
                data=None
            )

        task = await TaskService.toggle_complete(
            db=self.db,
            task_id=task_id,
            user_id=self.user_id,
            completed=True
        )

        return AIResponse(
            intent=Intent.COMPLETE,
            message=f"Done! I've marked '{task.title}' as complete.",
            action=AIAction(type=ActionType.NONE),
            data={
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "completed": task.completed
                }
            }
        )

    async def _uncomplete_task(self, data: Optional[dict[str, Any]]) -> AIResponse:
        """
        Mark a task as incomplete.

        FR-312: Toggle task completion status
        """
        task_id = self._extract_task_id(data)
        if not task_id:
            return AIResponse(
                intent=Intent.CLARIFY,
                message="Which task would you like to mark as incomplete?",
                action=AIAction(type=ActionType.NONE),
                data=None
            )

        task = await TaskService.toggle_complete(
            db=self.db,
            task_id=task_id,
            user_id=self.user_id,
            completed=False
        )

        return AIResponse(
            intent=Intent.UNCOMPLETE,
            message=f"I've marked '{task.title}' as incomplete.",
            action=AIAction(type=ActionType.NONE),
            data={
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "completed": task.completed
                }
            }
        )

    async def _update_task(
        self,
        action: AIAction,
        data: Optional[dict[str, Any]]
    ) -> AIResponse:
        """
        Update a task's title.

        FR-310: Update task via TaskService
        """
        task_id = self._extract_task_id(data)
        if not task_id:
            return AIResponse(
                intent=Intent.CLARIFY,
                message="Which task would you like to update?",
                action=AIAction(type=ActionType.NONE),
                data=None
            )

        payload = action.payload or {}
        new_title = payload.get("title", "").strip()

        if not new_title:
            return AIResponse(
                intent=Intent.CLARIFY,
                message="What would you like to rename the task to?",
                action=AIAction(type=ActionType.NONE),
                data={"task_id": str(task_id)}
            )

        task = await TaskService.update(
            db=self.db,
            task_id=task_id,
            user_id=self.user_id,
            title=new_title
        )

        return AIResponse(
            intent=Intent.UPDATE,
            message=f"I've updated the task to '{task.title}'.",
            action=AIAction(type=ActionType.NONE),
            data={
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "completed": task.completed
                }
            }
        )

    async def _delete_task(self, data: Optional[dict[str, Any]]) -> AIResponse:
        """
        Delete a task.

        FR-310: Delete task via TaskService
        Note: Delete confirmation should be handled by the AI before calling this
        """
        task_id = self._extract_task_id(data)
        if not task_id:
            return AIResponse(
                intent=Intent.CLARIFY,
                message="Which task would you like to delete?",
                action=AIAction(type=ActionType.NONE),
                data=None
            )

        # Get the task first to confirm it exists and get the title
        task = await TaskService.get(
            db=self.db,
            task_id=task_id,
            user_id=self.user_id
        )
        task_title = task.title

        await TaskService.delete(
            db=self.db,
            task_id=task_id,
            user_id=self.user_id
        )

        return AIResponse(
            intent=Intent.DELETE,
            message=f"I've deleted the task '{task_title}'.",
            action=AIAction(type=ActionType.NONE),
            data={"deleted_task_id": str(task_id), "deleted_task_title": task_title}
        )

    def _extract_task_id(self, data: Optional[dict[str, Any]]) -> Optional[UUID]:
        """
        Extract and validate task ID from data.

        Returns:
            UUID if valid task_id found, None otherwise
        """
        if not data:
            return None

        task_id = data.get("task_id")
        if not task_id:
            return None

        try:
            return UUID(str(task_id))
        except (ValueError, TypeError):
            logger.warning(f"Invalid task ID format: {task_id}")
            return None

    async def get_current_tasks(self) -> list[dict[str, Any]]:
        """
        Get all current tasks for AI context.

        Returns:
            List of task dictionaries for AI prompt context
        """
        tasks = await TaskService.list(db=self.db, user_id=self.user_id)
        return [
            {
                "id": str(task.id),
                "title": task.title,
                "completed": task.completed
            }
            for task in tasks
        ]
