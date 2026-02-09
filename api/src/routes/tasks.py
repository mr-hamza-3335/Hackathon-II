"""
Task management routes.
T053, T058, T066, T067, T073, T078, T091: Task endpoints per api-tasks.yaml contract
T-014: Integrate event publishing into task CRUD routes
T-017: Add sync event publishing to task CRUD routes
Requirements: FR-008-018, FR-022
Phase V: FR-001–006 (event publishing), FR-011 (non-blocking), FR-015 (API unchanged)
ADR-001: Route-level event publishing
"""
from functools import wraps
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..events import get_event_publisher
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
    T-014: Publish task.created event (FR-001)
    T-017: Publish sync event (FR-006)
    """
    task = await TaskService.create(db, current_user.id, request.title)

    # T-014, T-017: Publish lifecycle + sync events (fire-and-forget, ADR-001)
    publisher = get_event_publisher()
    await publisher.publish_task_event(task, "created")
    await publisher.publish_sync_event(str(task.id), str(current_user.id), "created")

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
    T-014: Publish task.updated event (FR-002)
    T-017: Publish sync event (FR-006)
    """
    task = await TaskService.update(
        db,
        task_id,
        current_user.id,
        title=request.title,
        completed=request.completed,
    )

    # T-014, T-017: Publish lifecycle + sync events (fire-and-forget, ADR-001)
    changes = {}
    if request.title is not None:
        changes["title"] = request.title
    if request.completed is not None:
        changes["completed"] = request.completed
    publisher = get_event_publisher()
    await publisher.publish_task_event(task, "updated", changes=changes)
    await publisher.publish_sync_event(str(task.id), str(current_user.id), "updated")

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
    T-014: Publish task.deleted event (FR-005)
    T-017: Publish sync event (FR-006)
    """
    # T-014: Capture task data before deletion for the event payload
    task = await TaskService.get(db, task_id, current_user.id)
    task_id_str = str(task.id)
    user_id_str = str(task.user_id)

    await TaskService.delete(db, task_id, current_user.id)

    # T-014, T-017: Publish lifecycle + sync events (fire-and-forget, ADR-001)
    publisher = get_event_publisher()
    await publisher.publish_task_event(task, "deleted")
    await publisher.publish_sync_event(task_id_str, user_id_str, "deleted")

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
    T-014: Publish task.completed event (FR-003)
    T-017: Publish sync event (FR-006)
    """
    task = await TaskService.toggle_complete(db, task_id, current_user.id, completed=True)

    # T-014, T-017: Publish lifecycle + sync events (fire-and-forget, ADR-001)
    publisher = get_event_publisher()
    await publisher.publish_task_event(task, "completed")
    await publisher.publish_sync_event(str(task.id), str(current_user.id), "completed")

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
    T-014: Publish task.uncompleted event (FR-004)
    T-017: Publish sync event (FR-006)
    """
    task = await TaskService.toggle_complete(db, task_id, current_user.id, completed=False)

    # T-014, T-017: Publish lifecycle + sync events (fire-and-forget, ADR-001)
    publisher = get_event_publisher()
    await publisher.publish_task_event(task, "uncompleted")
    await publisher.publish_sync_event(str(task.id), str(current_user.id), "uncompleted")

    return task
