"""
CloudEvents 1.0 schema models for event publishing.
T-010: Define CloudEvents schema models in api/src/events/schemas.py
Plan ref: Plan §1 (CloudEvents schema), §4.2 (schemas.py design)
Spec refs: FR-009 (CloudEvents 1.0), FR-010 (subject, datacontenttype, data), FR-014 (correlation ID)
Constitution VII: No direct Kafka — events published via Dapr Pub/Sub
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskEventData(BaseModel):
    """
    Payload for task lifecycle events on the `task-events` topic.

    T-010: TaskEventData per data-model.md TaskEvent entity
    FR-001–005: task.created/updated/completed/uncompleted/deleted
    """
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="Task owner UUID")
    action: str = Field(..., description="One of: created, updated, completed, uncompleted, deleted")
    title: Optional[str] = Field(None, description="Task title (present on created, updated)")
    completed: Optional[bool] = Field(None, description="Completion status (present on created, completed, uncompleted)")
    changes: Optional[dict] = Field(None, description="Changed fields map (present on updated)")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of the action")


class SyncEventData(BaseModel):
    """
    Lightweight payload for real-time sync events on the `task-updates` topic.

    T-010: SyncEventData per data-model.md SyncEvent entity
    FR-006: Sync event for every task mutation
    """
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="Task owner UUID")
    action: str = Field(..., description="One of: created, updated, completed, uncompleted, deleted")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of the action")


class ReminderEventData(BaseModel):
    """
    Payload for reminder events on the `reminders` topic.

    T-010: ReminderEventData per data-model.md ReminderEvent entity
    FR-007, FR-008: reminder.scheduled / reminder.rescheduled (future-ready)
    """
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="Task owner UUID")
    action: str = Field(..., description="One of: scheduled, rescheduled")
    due_date: str = Field(..., description="ISO 8601 due date")
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp of the action")


class CloudEvent(BaseModel):
    """
    CloudEvents 1.0 envelope model.

    T-010: CloudEvent per data-model.md and CloudEvents 1.0 specification
    FR-009: specversion, id, source, type, time required
    FR-010: subject (task ID), datacontenttype (application/json), data payload
    FR-014: traceid extension for correlation
    """
    specversion: str = Field(default="1.0", description="CloudEvents version")
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event ID")
    source: str = Field(default="pakaura/api", description="Event source URI")
    type: str = Field(..., description="Event type (e.g., task.created)")
    time: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        description="ISO 8601 UTC timestamp",
    )
    subject: str = Field(..., description="Task ID (UUID string)")
    datacontenttype: str = Field(default="application/json", description="Data content type")
    traceid: str = Field(default_factory=lambda: str(uuid4()), description="Correlation ID for tracing")
    data: dict = Field(..., description="Event-specific payload")
