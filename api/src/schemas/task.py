"""
Task request/response schemas.
T051: Create task request/response schemas in api/src/schemas/task.py per data-model.md
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class TaskCreateRequest(BaseModel):
    """Task creation request schema (FR-009, FR-016)."""
    title: str = Field(..., min_length=1, max_length=500, description="Task title (1-500 characters)")


class TaskUpdateRequest(BaseModel):
    """Task update request schema (FR-014, FR-016)."""
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Updated task title")
    completed: Optional[bool] = Field(None, description="Task completion status")


class TaskResponse(BaseModel):
    """Task response schema."""
    id: UUID
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Task list response schema."""
    tasks: list[TaskResponse]
    count: int
