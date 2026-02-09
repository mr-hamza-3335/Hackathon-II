"""
Dapr Pub/Sub event publisher for task lifecycle events.
T-011: Implement Dapr Pub/Sub publisher helper in api/src/events/publisher.py
T-015: Add logging & tracing metadata
T-016: Add safety guards (publish failures don't break API)
Plan ref: Plan §3 (publish flow), §4.2 (publisher design), §6 (error handling)
Spec refs: FR-011 (non-blocking), FR-012 (failure logging), FR-013 (Dapr pub/sub), FR-014 (correlation ID)
Constitution VII: No direct Kafka clients — all via Dapr sidecar HTTP API
ADR-001: Route-level event publishing
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

import httpx

from .schemas import CloudEvent, TaskEventData, SyncEventData, ReminderEventData

logger = logging.getLogger(__name__)

# T-011: Topic constants matching Stage 3 Kafka topic names
TOPIC_TASK_EVENTS = "task-events"
TOPIC_TASK_UPDATES = "task-updates"
TOPIC_REMINDERS = "reminders"


class EventPublisher:
    """
    Publishes CloudEvents to Kafka topics via the Dapr sidecar HTTP API.

    T-011: Core publisher class
    T-015: All methods include structured logging with correlation IDs
    T-016: All exceptions caught — never raises, never fails the API

    Constitution VII: Uses httpx → Dapr sidecar, no direct Kafka clients
    FR-011: Non-blocking, fire-and-forget
    FR-013: Dapr Pub/Sub abstraction (pubsub-kafka component)
    """

    def __init__(self, enabled: bool, http_port: int, pubsub_name: str, timeout: float):
        self._enabled = enabled
        self._base_url = f"http://localhost:{http_port}"
        self._pubsub_name = pubsub_name
        self._timeout = timeout

    def _build_cloud_event(
        self,
        event_type: str,
        subject: str,
        data: dict,
        traceid: Optional[str] = None,
    ) -> dict:
        """
        Build a CloudEvents 1.0 envelope.

        T-011: CloudEvent construction per data-model.md
        FR-009: specversion, id, source, type, time
        FR-010: subject, datacontenttype, data
        FR-014: traceid for correlation
        """
        event = CloudEvent(
            type=event_type,
            subject=subject,
            data=data,
            traceid=traceid or str(uuid4()),
        )
        return event.model_dump()

    async def _publish(self, topic: str, event: dict) -> None:
        """
        Publish a CloudEvent to a Dapr Pub/Sub topic.

        T-011: Core publish method
        T-016: ALL exceptions caught — NEVER raises
        FR-011: Non-blocking, fire-and-forget
        FR-012: Failure logged with full context
        FR-013: POST to Dapr sidecar /v1.0/publish/{pubsubname}/{topic}
        """
        # T-016: Skip if Dapr is disabled (local dev)
        if not self._enabled:
            logger.debug(
                "Event publish skipped (Dapr disabled): %s on %s",
                event.get("type", "unknown"),
                topic,
                extra={
                    "event_type": event.get("type"),
                    "topic": topic,
                    "task_id": event.get("subject"),
                    "correlation_id": event.get("traceid"),
                },
            )
            return

        url = f"{self._base_url}/v1.0/publish/{self._pubsub_name}/{topic}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    url,
                    json=event,
                    headers={"Content-Type": "application/cloudevents+json"},
                )

            if response.status_code == 204:
                # T-015: Success logging with structured fields
                logger.debug(
                    "Event published: %s on %s",
                    event.get("type"),
                    topic,
                    extra={
                        "event_type": event.get("type"),
                        "topic": topic,
                        "task_id": event.get("subject"),
                        "correlation_id": event.get("traceid"),
                        "dapr_status": 204,
                    },
                )
            else:
                # T-015: HTTP error logging
                logger.error(
                    "Event publish failed (HTTP %d): %s on %s — %s",
                    response.status_code,
                    event.get("type"),
                    topic,
                    response.text,
                    extra={
                        "event_type": event.get("type"),
                        "topic": topic,
                        "task_id": event.get("subject"),
                        "correlation_id": event.get("traceid"),
                        "dapr_status": response.status_code,
                        "dapr_response": response.text,
                    },
                )

        except httpx.ConnectError:
            # T-016: Dapr sidecar not available — log and continue
            logger.warning(
                "Dapr sidecar unavailable — event not published: %s on %s",
                event.get("type"),
                topic,
                extra={
                    "event_type": event.get("type"),
                    "topic": topic,
                    "task_id": event.get("subject"),
                    "correlation_id": event.get("traceid"),
                },
            )

        except httpx.TimeoutException:
            # T-016: Publish timed out — log and continue
            logger.warning(
                "Dapr publish timed out (%.1fs): %s on %s",
                self._timeout,
                event.get("type"),
                topic,
                extra={
                    "event_type": event.get("type"),
                    "topic": topic,
                    "task_id": event.get("subject"),
                    "correlation_id": event.get("traceid"),
                    "timeout": self._timeout,
                },
            )

        except Exception as exc:
            # T-016: Catch-all safety — NEVER let event publishing break the API
            logger.error(
                "Unexpected event publish error: %s on %s — %s",
                event.get("type"),
                topic,
                str(exc),
                extra={
                    "event_type": event.get("type"),
                    "topic": topic,
                    "task_id": event.get("subject"),
                    "correlation_id": event.get("traceid"),
                    "error": str(exc),
                },
            )

    async def publish_task_event(
        self,
        task,
        action: str,
        changes: Optional[dict] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Publish a task lifecycle event to the `task-events` topic.

        T-014: Called from route handlers after TaskService succeeds
        FR-001–005: task.created/updated/completed/uncompleted/deleted
        ADR-001: Route-level publishing — fires after service call, before response

        Args:
            task: Task ORM model (has id, user_id, title, completed)
            action: One of "created", "updated", "completed", "uncompleted", "deleted"
            changes: Optional dict of changed fields (for "updated" action)
            correlation_id: Optional correlation ID (generated if not provided)
        """
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        task_id = str(task.id)
        user_id = str(task.user_id)
        cid = correlation_id or str(uuid4())

        data = TaskEventData(
            task_id=task_id,
            user_id=user_id,
            action=action,
            title=task.title if action in ("created", "updated") else None,
            completed=task.completed if action in ("created", "completed", "uncompleted") else None,
            changes=changes,
            timestamp=now,
        )

        event = self._build_cloud_event(
            event_type=f"task.{action}",
            subject=task_id,
            data=data.model_dump(exclude_none=True),
            traceid=cid,
        )

        await self._publish(TOPIC_TASK_EVENTS, event)

    async def publish_task_event_from_dict(
        self,
        task_dict: dict,
        action: str,
        user_id: str,
        changes: Optional[dict] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Publish a task lifecycle event from a dict (for MCP layer).

        T-019: Called from mcp_server/task_operations.py after DB operations
        FR-001–005: Same events as publish_task_event but from dict data

        Args:
            task_dict: Dict with task fields (id, title, completed)
            action: One of "created", "updated", "completed", "uncompleted", "deleted"
            user_id: User ID string
            changes: Optional dict of changed fields
            correlation_id: Optional correlation ID
        """
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        task_id = str(task_dict.get("id", ""))
        cid = correlation_id or str(uuid4())

        data = TaskEventData(
            task_id=task_id,
            user_id=user_id,
            action=action,
            title=task_dict.get("title") if action in ("created", "updated") else None,
            completed=task_dict.get("completed") if action in ("created", "completed", "uncompleted") else None,
            changes=changes,
            timestamp=now,
        )

        event = self._build_cloud_event(
            event_type=f"task.{action}",
            subject=task_id,
            data=data.model_dump(exclude_none=True),
            traceid=cid,
        )

        await self._publish(TOPIC_TASK_EVENTS, event)

    async def publish_sync_event(
        self,
        task_id: str,
        user_id: str,
        action: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Publish a lightweight sync event to the `task-updates` topic.

        T-017: Called from route handlers alongside lifecycle events
        FR-006: Sync event for every task mutation

        Args:
            task_id: Task UUID string
            user_id: User UUID string
            action: One of "created", "updated", "completed", "uncompleted", "deleted"
            correlation_id: Optional correlation ID
        """
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        cid = correlation_id or str(uuid4())

        data = SyncEventData(
            task_id=task_id,
            user_id=user_id,
            action=action,
            timestamp=now,
        )

        event = self._build_cloud_event(
            event_type="sync.task",
            subject=task_id,
            data=data.model_dump(),
            traceid=cid,
        )

        await self._publish(TOPIC_TASK_UPDATES, event)

    async def publish_reminder_event(
        self,
        task_id: str,
        user_id: str,
        action: str,
        due_date: str,
        correlation_id: Optional[str] = None,
    ) -> None:
        """
        Publish a reminder event to the `reminders` topic.

        T-018: Future-ready — only fires when Task model has due_date field
        FR-007: reminder.scheduled
        FR-008: reminder.rescheduled

        Args:
            task_id: Task UUID string
            user_id: User UUID string
            action: One of "scheduled", "rescheduled"
            due_date: ISO 8601 due date string
            correlation_id: Optional correlation ID
        """
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        cid = correlation_id or str(uuid4())

        data = ReminderEventData(
            task_id=task_id,
            user_id=user_id,
            action=action,
            due_date=due_date,
            timestamp=now,
        )

        event = self._build_cloud_event(
            event_type=f"reminder.{action}",
            subject=task_id,
            data=data.model_dump(),
            traceid=cid,
        )

        await self._publish(TOPIC_REMINDERS, event)


# T-012: Module-level singleton and getter
_publisher_instance: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """
    Get the singleton EventPublisher instance.

    T-012: Lazy initialization from app settings
    Reads Dapr config from Settings on first call.
    """
    global _publisher_instance
    if _publisher_instance is None:
        from ..config import get_settings
        settings = get_settings()
        _publisher_instance = EventPublisher(
            enabled=settings.dapr_enabled,
            http_port=settings.dapr_http_port,
            pubsub_name=settings.dapr_pubsub_name,
            timeout=settings.dapr_publish_timeout,
        )
    return _publisher_instance
