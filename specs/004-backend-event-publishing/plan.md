# Implementation Plan: Backend Event Publishing

**Branch**: `004-backend-event-publishing` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-backend-event-publishing/spec.md`

## Summary

Implement event publishing for all task lifecycle actions via Dapr Pub/Sub. The API publishes CloudEvents 1.0-compliant events to three Kafka topics (`task-events`, `task-updates`, `reminders`) through the Dapr sidecar HTTP API. Event publishing is non-blocking and fault-tolerant — failures are logged but never impact API responses.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, httpx (v0.28.1, already installed), Pydantic v2
**Storage**: N/A (events are transient — published to Kafka via Dapr, not stored in PostgreSQL)
**Testing**: pytest with httpx mocking
**Target Platform**: Kubernetes (Minikube local, OKE/AKS/GKE production)
**Project Type**: Web application (backend API service)
**Performance Goals**: Event publishing adds <50ms overhead (non-blocking, async)
**Constraints**: No direct Kafka clients (Constitution VII), fire-and-forget only
**Scale/Scope**: 5 event types × 3 topics, ~10 files modified/created

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| VII | No direct Kafka clients | PASS | Uses httpx → Dapr sidecar HTTP API |
| VIII | All async via Dapr | PASS | Pub/Sub via Dapr, no direct service calls |
| IX | No hard-coded secrets | PASS | No secrets involved in event publishing |
| X | Kubernetes-first | PASS | Dapr sidecar is a K8s pattern; graceful degradation without it |
| XI | Cloud-agnostic | PASS | Dapr abstracts the broker; swappable without code changes |
| XII | No manual coding | PASS | All work traced to task IDs |
| XIII | Observability | PASS | Structured JSON logging with correlation IDs |
| XIV | Event-driven | PASS | This feature IS the event publishing layer |

**Gate result**: ALL PASS — proceed.

## §1. CloudEvents 1.0 Schema

### §1.1 Required Attributes (per CloudEvents spec)

```
specversion: "1.0"                              # CloudEvents version
id:          "<uuid4>"                           # Unique per event
source:      "pakaura/api"                       # Event origin
type:        "task.created|task.updated|..."     # Event type
time:        "2026-02-09T14:30:00Z"             # ISO 8601 UTC
```

### §1.2 Optional/Extension Attributes

```
subject:         "<task-uuid>"                   # Task ID
datacontenttype: "application/json"              # Always JSON
traceid:         "<correlation-uuid>"             # Tracing (custom extension)
```

### §1.3 Data Payload Structure

See [data-model.md](data-model.md) for complete field definitions per event type.

## §2. Event Naming Conventions & Topic Mapping

### §2.1 Event Types

| Event Type | Action | Topic | Description |
|------------|--------|-------|-------------|
| `task.created` | Task created | `task-events` | New task added |
| `task.updated` | Title changed | `task-events` | Task field modified |
| `task.completed` | Marked complete | `task-events` | Completion toggled on |
| `task.uncompleted` | Marked incomplete | `task-events` | Completion toggled off |
| `task.deleted` | Task removed | `task-events` | Task permanently deleted |
| `sync.task` | Any mutation | `task-updates` | Lightweight sync for WebSocket |
| `reminder.scheduled` | Due date set | `reminders` | New reminder (future-ready) |
| `reminder.rescheduled` | Due date changed | `reminders` | Updated reminder (future-ready) |

### §2.2 Naming Rules

- **Domain prefix**: `task.` for lifecycle, `sync.` for broadcasting, `reminder.` for scheduling
- **Past tense action**: `created`, `updated`, `completed`, `uncompleted`, `deleted`
- **Topic names**: Lowercase, hyphenated, matching Stage 3 Kafka topic names exactly

## §3. Dapr Pub/Sub Publish Flow

### §3.1 Publish API

```
POST http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/pubsub-kafka/{topic}
Content-Type: application/cloudevents+json

{CloudEvents JSON body}
```

- Dapr component name: `pubsub-kafka` (matches Stage 3 component)
- Topics: `task-events`, `task-updates`, `reminders`
- Content mode: Structured (full CloudEvents JSON in body)
- Response: 204 No Content on success

### §3.2 Publish Flow

```
API Handler → TaskService.method() → success
                                         ↓
                              EventPublisher.publish()
                                         ↓
                              Build CloudEvent envelope
                                         ↓
                              httpx.AsyncClient.post() → Dapr sidecar
                                         ↓
                              Dapr → Kafka topic
                                         ↓
                              Log result (success or failure)
```

### §3.3 Graceful Degradation

```
if DAPR_ENABLED == false:
    log event at DEBUG level → return (no HTTP call)

if DAPR_ENABLED == true:
    try:
        POST to Dapr sidecar (2s timeout)
        if 204: log DEBUG "published"
        else:   log ERROR "publish failed" with status + body
    except ConnectionError:
        log WARNING "Dapr sidecar unavailable"
    except TimeoutError:
        log WARNING "Dapr publish timed out"
    # NEVER raise — API response is unaffected
```

## §4. Backend Module Structure

### §4.1 New Files

```
api/src/events/
├── __init__.py              # Module init, exports EventPublisher
├── schemas.py               # CloudEvent, TaskEventData, SyncEventData, ReminderEventData
└── publisher.py             # EventPublisher class with publish methods
```

### §4.2 Module Responsibilities

**`schemas.py`** — Pydantic models for CloudEvents and event data payloads:
- `CloudEvent`: Base CloudEvents 1.0 envelope (specversion, id, source, type, time, subject, datacontenttype, traceid, data)
- `TaskEventData`: Payload for task lifecycle events (task_id, user_id, action, title, completed, changes, timestamp)
- `SyncEventData`: Lightweight payload for sync events (task_id, user_id, action, timestamp)
- `ReminderEventData`: Payload for reminder events (task_id, user_id, action, due_date, timestamp)

**`publisher.py`** — `EventPublisher` singleton with methods:
- `publish_task_event(task, action, changes=None)`: Builds and publishes to `task-events`
- `publish_sync_event(task_id, user_id, action)`: Builds and publishes to `task-updates`
- `publish_reminder_event(task_id, user_id, action, due_date)`: Builds and publishes to `reminders`
- `_publish(topic, event)`: Internal method that calls Dapr sidecar HTTP API
- `_build_cloud_event(type, subject, data)`: Constructs CloudEvents envelope

**`__init__.py`** — Exports:
- `EventPublisher` (the publisher instance)
- `get_event_publisher()` function for dependency injection

### §4.3 Modified Files

| File | Change | FR Refs |
|------|--------|---------|
| `api/src/config.py` | Add `dapr_enabled`, `dapr_http_port` settings | FR-013 |
| `api/src/routes/tasks.py` | Add event publishing calls after each CRUD handler | FR-001–006, FR-011 |
| `api/src/mcp_server/task_operations.py` | Add event publishing calls after each DB operation | FR-001–006 |
| `api/src/events/__init__.py` | New module init | — |
| `api/src/events/schemas.py` | New event schema models | FR-009, FR-010, FR-014 |
| `api/src/events/publisher.py` | New publisher implementation | FR-011, FR-012, FR-013 |

## §5. Integration Points

### §5.1 Task CRUD Routes (`api/src/routes/tasks.py`)

Each route handler gets event publishing added AFTER the service call returns successfully:

| Route | Service Call | Events Published |
|-------|-------------|-----------------|
| `POST /tasks` | `TaskService.create()` | `task.created` → task-events, `sync.task` → task-updates |
| `PATCH /tasks/{id}` | `TaskService.update()` | `task.updated` → task-events, `sync.task` → task-updates |
| `DELETE /tasks/{id}` | `TaskService.delete()` | `task.deleted` → task-events, `sync.task` → task-updates |
| `POST /tasks/{id}/complete` | `TaskService.toggle_complete(True)` | `task.completed` → task-events, `sync.task` → task-updates |
| `POST /tasks/{id}/uncomplete` | `TaskService.toggle_complete(False)` | `task.uncompleted` → task-events, `sync.task` → task-updates |

**Pattern** (in each handler):

```python
# 1. Perform CRUD operation (existing code, unchanged)
task = await TaskService.create(db, current_user.id, request.title)

# 2. Publish events (NEW — fire-and-forget, non-blocking)
publisher = get_event_publisher()
await publisher.publish_task_event(task, "created")
await publisher.publish_sync_event(str(task.id), str(current_user.id), "created")

# 3. Return response (existing code, unchanged)
return task
```

### §5.2 MCP Server Task Operations (`api/src/mcp_server/task_operations.py`)

Each operation gets event publishing added AFTER the DB operation succeeds:

| Method | Events Published |
|--------|-----------------|
| `add_task()` | `task.created` → task-events, `sync.task` → task-updates |
| `update_task()` | `task.updated` → task-events, `sync.task` → task-updates |
| `complete_task()` | `task.completed` → task-events, `sync.task` → task-updates |
| `uncomplete_task()` | `task.uncompleted` → task-events, `sync.task` → task-updates |
| `delete_task()` | `task.deleted` → task-events, `sync.task` → task-updates |
| `clear_completed()` | `task.deleted` (one per deleted task) → task-events, `sync.task` → task-updates |

**Pattern** (in each method, after successful DB operation):

```python
# After successful DB operation
if result["success"]:
    publisher = get_event_publisher()
    await publisher.publish_task_event_from_dict(result["task"], "created")
    await publisher.publish_sync_event(task_id, user_id, "created")
```

### §5.3 Reminder Events (Future-Ready)

No integration point exists today because the Task model has no `due_date` field. The publisher method `publish_reminder_event()` will be implemented but not called from any handler. When the `due_date` field is added:

- `create_task()` → if `due_date` is set, publish `reminder.scheduled`
- `update_task()` → if `due_date` changed, publish `reminder.rescheduled`

## §6. Error Handling & Observability

### §6.1 Error Handling Strategy

| Scenario | Behavior | Log Level |
|----------|----------|-----------|
| Dapr disabled (`DAPR_ENABLED=false`) | Skip publish, log event content | DEBUG |
| Publish success (HTTP 204) | Continue | DEBUG |
| Publish HTTP error (non-204) | Log and continue | ERROR |
| Dapr sidecar unreachable | Log and continue | WARNING |
| Publish timeout (>2s) | Log and continue | WARNING |
| Event serialization error | Log and continue | ERROR |

**Critical rule**: The `try/except` in `_publish()` catches ALL exceptions. The API handler NEVER sees an exception from event publishing.

### §6.2 Structured Logging

All event-related logs use structured fields (Constitution XIII):

```python
logger.info(
    "Event published",
    extra={
        "event_type": "task.created",
        "topic": "task-events",
        "task_id": "f47ac10b-...",
        "user_id": "123e4567-...",
        "correlation_id": "9876fedc-...",
        "dapr_status": 204,
    }
)
```

### §6.3 Correlation ID Flow

```
HTTP Request → generate correlation_id (uuid4)
  → pass to EventPublisher
    → included in CloudEvent envelope as `traceid` extension
      → propagated through Kafka to all consumers
        → appears in all downstream service logs
```

## §7. Sequence Diagrams

### §7.1 Task Created → Kafka

```
User          API Route         TaskService      EventPublisher     Dapr Sidecar      Kafka
 │                │                  │                │                 │               │
 │ POST /tasks    │                  │                │                 │               │
 │───────────────>│                  │                │                 │               │
 │                │ create(db,uid,t) │                │                 │               │
 │                │─────────────────>│                │                 │               │
 │                │                  │ INSERT + flush │                 │               │
 │                │                  │───────────┐    │                 │               │
 │                │    Task object   │<──────────┘    │                 │               │
 │                │<─────────────────│                │                 │               │
 │                │                  │                │                 │               │
 │                │ publish_task_event(task,"created") │                │               │
 │                │─────────────────────────────────>│                 │               │
 │                │                  │                │ POST /publish/  │               │
 │                │                  │                │ pubsub-kafka/   │               │
 │                │                  │                │ task-events     │               │
 │                │                  │                │────────────────>│               │
 │                │                  │                │                 │ Produce msg   │
 │                │                  │                │                 │──────────────>│
 │                │                  │                │    204 OK       │               │
 │                │                  │                │<────────────────│               │
 │                │                  │                │                 │               │
 │                │ publish_sync_event(id,uid,"created")               │               │
 │                │─────────────────────────────────>│                 │               │
 │                │                  │                │ POST /publish/  │               │
 │                │                  │                │ pubsub-kafka/   │               │
 │                │                  │                │ task-updates    │               │
 │                │                  │                │────────────────>│               │
 │                │                  │                │                 │ Produce msg   │
 │                │                  │                │                 │──────────────>│
 │                │                  │                │    204 OK       │               │
 │                │                  │                │<────────────────│               │
 │                │                  │                │                 │               │
 │  201 Created   │                  │                │                 │               │
 │<───────────────│                  │                │                 │               │
```

### §7.2 Task Completed → Recurring/Reminder Pipeline

```
User          API Route         TaskService      EventPublisher     Dapr Sidecar      Kafka
 │                │                  │                │                 │               │
 │ POST /{id}/    │                  │                │                 │               │
 │ complete       │                  │                │                 │               │
 │───────────────>│                  │                │                 │               │
 │                │ toggle_complete  │                │                 │               │
 │                │ (db,id,uid,True) │                │                 │               │
 │                │─────────────────>│                │                 │               │
 │                │                  │ UPDATE + flush │                 │               │
 │                │   Task(done=T)   │<──────────┐    │                 │               │
 │                │<─────────────────│           │    │                 │               │
 │                │                  │                │                 │               │
 │                │ publish_task_event(task,"completed")               │               │
 │                │─────────────────────────────────>│                 │               │
 │                │                  │                │ POST task-events│               │
 │                │                  │                │────────────────>│               │
 │                │                  │                │                 │──────────────>│
 │                │                  │                │   204           │               │
 │                │                  │                │<────────────────│     ┌─────────┤
 │                │                  │                │                 │     │Recurring│
 │                │                  │                │                 │     │Service   │
 │                │                  │                │                 │     │consumes  │
 │                │                  │                │                 │     │task.     │
 │                │                  │                │                 │     │completed │
 │                │ publish_sync_event(id,uid,"completed")             │     └─────────┤
 │                │─────────────────────────────────>│                 │               │
 │                │                  │                │ POST task-updates               │
 │                │                  │                │────────────────>│──────────────>│
 │                │                  │                │   204           │     ┌─────────┤
 │                │                  │                │<────────────────│     │WebSocket │
 │                │                  │                │                 │     │Gateway   │
 │                │                  │                │                 │     │consumes  │
 │  200 OK        │                  │                │                 │     └─────────┤
 │<───────────────│                  │                │                 │               │
```

### §7.3 Task Updated → WebSocket Sync

```
User          API Route         TaskService      EventPublisher     Dapr Sidecar      Kafka       WS Gateway
 │                │                  │                │                 │               │              │
 │ PATCH /{id}    │                  │                │                 │               │              │
 │ {title:"new"}  │                  │                │                 │               │              │
 │───────────────>│                  │                │                 │               │              │
 │                │ update(db,id,    │                │                 │               │              │
 │                │  uid,title="new")│                │                 │               │              │
 │                │─────────────────>│                │                 │               │              │
 │                │                  │ UPDATE + flush │                 │               │              │
 │                │   Task(updated)  │<──────────┐    │                 │               │              │
 │                │<─────────────────│           │    │                 │               │              │
 │                │                  │                │                 │               │              │
 │                │ publish_task_event(task,"updated",changes)         │               │              │
 │                │─────────────────────────────────>│                 │               │              │
 │                │                  │                │ POST task-events│               │              │
 │                │                  │                │────────────────>│──────────────>│              │
 │                │                  │                │   204           │               │              │
 │                │                  │                │<────────────────│               │              │
 │                │                  │                │                 │               │              │
 │                │ publish_sync_event(id,uid,"updated")               │               │              │
 │                │─────────────────────────────────>│                 │               │              │
 │                │                  │                │ POST task-      │               │              │
 │                │                  │                │ updates         │               │              │
 │                │                  │                │────────────────>│──────────────>│              │
 │                │                  │                │   204           │               │  Dapr sub    │
 │                │                  │                │<────────────────│               │─────────────>│
 │                │                  │                │                 │               │              │
 │                │                  │                │                 │               │  Push to     │
 │                │                  │                │                 │               │  connected   │
 │  200 OK        │                  │                │                 │               │  clients     │
 │<───────────────│                  │                │                 │               │              │
```

## §8. Configuration Changes

### §8.1 New Settings (`api/src/config.py`)

```python
# Dapr Configuration (Phase V)
dapr_enabled: bool = False          # Enable event publishing via Dapr
dapr_http_port: int = 3500          # Dapr sidecar HTTP port
dapr_pubsub_name: str = "pubsub-kafka"  # Dapr pubsub component name
dapr_publish_timeout: float = 2.0   # HTTP timeout for publish calls (seconds)
```

### §8.2 Helm Values Updates

Add to `values.yaml` and `values-local.yaml`:
```yaml
api:
  env:
    DAPR_ENABLED: "true"      # Enable in K8s
    # DAPR_HTTP_PORT is auto-injected by Dapr
```

## Project Structure

### Documentation (this feature)

```text
specs/004-backend-event-publishing/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Research decisions
├── data-model.md        # Event schemas
├── quickstart.md        # Developer guide
├── contracts/
│   └── dapr-publish-api.md  # Dapr HTTP API contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
api/src/
├── config.py                    # MODIFIED: Add Dapr settings
├── events/                      # NEW: Event publishing module
│   ├── __init__.py              # Module init, exports
│   ├── schemas.py               # CloudEvent + data payload models
│   └── publisher.py             # EventPublisher (Dapr HTTP client)
├── routes/
│   └── tasks.py                 # MODIFIED: Add event publishing calls
├── mcp_server/
│   └── task_operations.py       # MODIFIED: Add event publishing calls
└── ...                          # Unchanged files
```

**Structure Decision**: Extend existing `api/src/` with a new `events/` module. No new top-level directories or services. This is the smallest viable change — a helper module inside the existing API service.

## Complexity Tracking

No constitution violations to justify. All design decisions align with principles VII–XIV.

## Readiness Checklist for `/sp.tasks`

| # | Check | Status |
|---|-------|--------|
| 1 | Spec reviewed and complete (no NEEDS CLARIFICATION) | PASS |
| 2 | Constitution check passes (all 8 principles) | PASS |
| 3 | Research decisions documented (5 decisions) | PASS |
| 4 | Data model defined (3 event schemas + samples) | PASS |
| 5 | API contract documented (Dapr publish API) | PASS |
| 6 | Integration points identified (routes + MCP) | PASS |
| 7 | Error handling strategy defined | PASS |
| 8 | Sequence diagrams for all 3 flows | PASS |
| 9 | File layout and module structure defined | PASS |
| 10 | No new external dependencies required | PASS |

**Result**: Ready for `/sp.tasks`.
