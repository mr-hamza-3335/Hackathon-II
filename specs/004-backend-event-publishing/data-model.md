# Data Model: Backend Event Publishing

**Branch**: `004-backend-event-publishing` | **Date**: 2026-02-09

## Overview

This feature introduces event schemas (not database models). Events are transient messages published to Kafka topics via Dapr — they are NOT persisted in PostgreSQL. No database schema changes are required.

## Event Schemas

### CloudEvent Envelope (Base)

All events conform to CloudEvents 1.0 specification.

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `specversion` | string | Yes | Always `"1.0"` |
| `id` | string (UUID) | Yes | Unique event ID (generated per event) |
| `source` | string (URI) | Yes | Always `"pakaura/api"` |
| `type` | string | Yes | Event type (e.g., `task.created`) |
| `time` | string (ISO 8601) | Yes | Event timestamp in UTC |
| `subject` | string | Yes | Task ID (UUID string) |
| `datacontenttype` | string | Yes | Always `"application/json"` |
| `traceid` | string (UUID) | Extension | Correlation ID for tracing |
| `data` | object | Yes | Event-specific payload |

### TaskEvent Data Payload

Published to `task-events` topic for types: `task.created`, `task.updated`, `task.completed`, `task.uncompleted`, `task.deleted`

| Field | Type | Present In | Description |
|-------|------|------------|-------------|
| `task_id` | string (UUID) | All | The task's unique identifier |
| `user_id` | string (UUID) | All | The task owner's user ID |
| `action` | string | All | One of: `created`, `updated`, `completed`, `uncompleted`, `deleted` |
| `title` | string | created, updated | Task title (current or new value) |
| `completed` | boolean | created, completed, uncompleted | Completion status after the action |
| `changes` | object | updated | Map of changed fields: `{"title": "new value"}` |
| `timestamp` | string (ISO 8601) | All | When the action occurred |

### SyncEvent Data Payload

Published to `task-updates` topic for all task mutations. Lightweight payload for WebSocket broadcasting.

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string (UUID) | The task's unique identifier |
| `user_id` | string (UUID) | The task owner's user ID |
| `action` | string | One of: `created`, `updated`, `completed`, `uncompleted`, `deleted` |
| `timestamp` | string (ISO 8601) | When the action occurred |

### ReminderEvent Data Payload (Future-Ready)

Published to `reminders` topic. Only fires when the Task model has a `due_date` field.

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string (UUID) | The task's unique identifier |
| `user_id` | string (UUID) | The task owner's user ID |
| `action` | string | One of: `scheduled`, `rescheduled` |
| `due_date` | string (ISO 8601) | The task's due date |
| `timestamp` | string (ISO 8601) | When the action occurred |

## Event Type → Topic Mapping

| Event Type | Topic | Consumer Groups |
|------------|-------|-----------------|
| `task.created` | `task-events` | recurring-svc, audit-svc, notification-svc |
| `task.updated` | `task-events` | audit-svc, notification-svc |
| `task.completed` | `task-events` | recurring-svc, audit-svc, notification-svc |
| `task.uncompleted` | `task-events` | audit-svc |
| `task.deleted` | `task-events` | audit-svc, notification-svc |
| `sync.*` | `task-updates` | websocket-gw |
| `reminder.scheduled` | `reminders` | audit-svc, notification-svc, websocket-gw |
| `reminder.rescheduled` | `reminders` | audit-svc, notification-svc, websocket-gw |

## Sample Event Payloads

### task.created

```json
{
  "specversion": "1.0",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source": "pakaura/api",
  "type": "task.created",
  "time": "2026-02-09T14:30:00Z",
  "subject": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "datacontenttype": "application/json",
  "traceid": "9876fedc-ba09-8765-4321-0fedcba98765",
  "data": {
    "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "action": "created",
    "title": "Buy groceries",
    "completed": false,
    "timestamp": "2026-02-09T14:30:00Z"
  }
}
```

### task.completed

```json
{
  "specversion": "1.0",
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "source": "pakaura/api",
  "type": "task.completed",
  "time": "2026-02-09T15:00:00Z",
  "subject": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "datacontenttype": "application/json",
  "traceid": "abcd1234-ef56-7890-abcd-ef1234567890",
  "data": {
    "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "action": "completed",
    "completed": true,
    "timestamp": "2026-02-09T15:00:00Z"
  }
}
```

### Sync Event (task-updates topic)

```json
{
  "specversion": "1.0",
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "source": "pakaura/api",
  "type": "sync.task",
  "time": "2026-02-09T15:00:00Z",
  "subject": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "datacontenttype": "application/json",
  "traceid": "abcd1234-ef56-7890-abcd-ef1234567890",
  "data": {
    "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "action": "completed",
    "timestamp": "2026-02-09T15:00:00Z"
  }
}
```

## Existing Models (Unchanged)

No changes to existing database models. The `Task` model (`api/src/models/task.py`) remains as-is:
- `id`: UUID primary key
- `user_id`: UUID foreign key
- `title`: String(500)
- `completed`: Boolean
- `created_at` / `updated_at`: DateTime (from TimestampMixin)
