"""
Task management routes.
T053, T058, T066, T067, T073, T078, T091: Task endpoints per api-tasks.yaml contract
Requirements: FR-008-018, FR-022
"""
from functools import wraps
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse
from ..schemas.common import MessageResponse
from ..services import TaskService
from ..services.task_service import AuthorizationError, NotFoundError
from ..middleware.auth import get_current_user
from ..models import User

router = APIRouter()


def handle_task_errors(func):
    """Decorator to handle common task service errors."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NotFoundError:
            raise HTTPException(
                status_code=404,
                detail={"error": {
                    "code": "NOT_FOUND",
                    "message": "Task not found",
                    "details": [],
                }},
            )
        except AuthorizationError:
            # T087: Authorization error for cross-user access
            raise HTTPException(
                status_code=403,
                detail={"error": {
                    "code": "AUTHORIZATION_ERROR",
                    "message": "Access denied",
                    "details": [],
                }},
            )
    return wrapper


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task.

    FR-009: Allow authenticated users to create tasks with a title
    FR-010: Auto-generate unique IDs for each task
    FR-016: Validate task titles (1-500 characters, non-empty)
    FR-017: Persist all task data to the database
    FR-018: Associate each task with its owner's user ID
    """
    task = await TaskService.create(db, current_user.id, request.title)
    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all tasks for the current user.

    FR-008: Restrict task access to the task owner only
    FR-011: Allow authenticated users to view their task list
    """
    tasks = await TaskService.list(db, current_user.id, completed)
    return {"tasks": tasks, "count": len(tasks)}


@router.get("/{task_id}", response_model=TaskResponse)
@handle_task_errors
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific task.

    FR-008: Restrict task access to the task owner only
    """
    task = await TaskService.get(db, task_id, current_user.id)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
@handle_task_errors
async def update_task(
    task_id: UUID,
    request: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a task.

    FR-014: Allow authenticated users to update task titles
    FR-012: Allow authenticated users to mark tasks complete
    FR-013: Allow authenticated users to mark tasks incomplete
    FR-016: Validate task titles (1-500 characters, non-empty)
    FR-008: Restrict task access to the task owner only
    """
    task = await TaskService.update(
        db,
        task_id,
        current_user.id,
        title=request.title,
        completed=request.completed,
    )
    return task


@router.delete("/{task_id}", response_model=MessageResponse)
@handle_task_errors
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a task.

    FR-015: Allow authenticated users to delete tasks
    FR-008: Restrict task access to the task owner only
    """
    await TaskService.delete(db, task_id, current_user.id)
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/complete", response_model=TaskResponse)
@handle_task_errors
async def complete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a task as complete.

    FR-012: Allow authenticated users to mark tasks complete
    """
    task = await TaskService.toggle_complete(db, task_id, current_user.id, completed=True)
    return task


@router.post("/{task_id}/uncomplete", response_model=TaskResponse)
@handle_task_errors
async def uncomplete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a task as incomplete.

    FR-013: Allow authenticated users to mark tasks incomplete
    """
    task = await TaskService.toggle_complete(db, task_id, current_user.id, completed=False)
    return task
