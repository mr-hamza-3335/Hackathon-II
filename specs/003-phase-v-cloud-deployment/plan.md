# Implementation Plan: Phase V – Advanced Cloud Deployment

**Branch**: `003-phase-v-cloud-deployment` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-phase-v-cloud-deployment/spec.md`
**Type**: Architecture & Design Only (no code, no tasks)

## Summary

Extend the PakAura AI Task Manager with advanced task features (recurring tasks, due dates/reminders, priorities, tags, search/filter/sort, activity log, real-time sync) and an event-driven architecture using Kafka + Dapr. Deploy to Oracle OKE (production) and Minikube (local) with CI/CD via GitHub Actions and centralized monitoring.

## Technical Context

**Language/Version**: Python 3.11 (API/services), Node.js 20 (Frontend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy (async), Alembic, Next.js 14, Dapr SDK (Python + JS), Apache Kafka, Cohere AI SDK
**Storage**: PostgreSQL 15 (primary), Kafka (event stream, 7-day retention), Dapr State Store (caching)
**Testing**: pytest (Python services), Jest/Vitest (Frontend), k6 (load testing)
**Target Platform**: Kubernetes (Minikube local, Oracle OKE production)
**Project Type**: Web application (microservices)
**Performance Goals**: <3s real-time sync (SC-005), <2s search (SC-004), <60s reminder delivery (SC-002)
**Constraints**: <512Mi per API service pod, <256Mi per lightweight service pod, single Kafka broker locally
**Scale/Scope**: Single-user demo workload; architecture supports horizontal scaling

## Constitution Check

*GATE: Must pass before implementation. Re-checked after design.*

| Gate | Requirement | Status |
| ---- | ----------- | ------ |
| I. Spec-Driven | Feature defined in spec before implementation | PASS — spec.md complete with 51 FRs, 14 SCs |
| II. Single Repo | All code in one repository | PASS — same repo as Phases I–IV |
| III. Evolution | Extends previous phases, no rewrites | PASS — extends Phase II schema, Phase III chatbot, Phase IV Helm |
| IV. Single Source | Requirements in /specs/ | PASS — spec.md is authoritative |
| V. Clean Architecture | Separation of concerns | PASS — see Project Structure below |
| VI. Quality Bar | Production-grade, no over-engineering | PASS — microservices justified by event-driven requirements |
| Phase V: Kafka | Kafka for reminders, recurring, audit, real-time | PASS — all four use cases mapped to Kafka topics |
| Phase V: Reliability | Tolerate restarts, durable/replayable events | PASS — 7-day Kafka retention, PG activity log permanent |

No violations. No complexity justifications needed.

---

## 1. System Architecture

### 1.1 Architecture Overview

The system is a **Kubernetes-based microservices architecture** with **event-driven communication** via Kafka and **Dapr sidecars** per service providing infrastructure abstraction.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Kubernetes Cluster                                  │
│                      (Minikube / Oracle OKE)                                 │
│                                                                             │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Frontend   │  │  Chat API  │  │ Notification │  │  Recurring   │        │
│  │  (Next.js)  │  │  (FastAPI  │  │   Service    │  │   Service    │        │
│  │             │  │  + MCP)    │  │   + Dapr     │  │   + Dapr     │        │
│  │  No sidecar │  │  + Dapr    │  │              │  │              │        │
│  └──────┬──────┘  └──────┬─────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                │                │                  │                │
│         │         ┌──────┴────────────────┴──────────────────┘                │
│         │         │          Dapr Sidecar Layer                               │
│         │         │  (Pub/Sub, State, Secrets, Jobs, Service Invocation)      │
│         │         │                                                          │
│         │         └──────┬────────────────┬──────────────────┐                │
│         │                │                │                  │                │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐  ┌───────┴──────┐        │
│  │  WebSocket  │  │    Kafka    │  │ PostgreSQL  │  │   Audit      │        │
│  │  Gateway    │  │  (single /  │  │     15      │  │   Service    │        │
│  │  + Dapr     │  │   managed)  │  │             │  │   + Dapr     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────┘        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────┐           │
│  │                    Monitoring Stack                            │           │
│  │            (Prometheus + Grafana + Loki + Promtail)           │           │
│  └───────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Communication Patterns

**Synchronous (REST via Dapr Service Invocation)**:
- Frontend → Chat API (user requests)
- Frontend → WebSocket Gateway (WS upgrade)
- Recurring Service → Chat API (create next task instance)

**Asynchronous (Event-Driven via Kafka through Dapr Pub/Sub)**:
- Chat API → Kafka → Recurring Service, Audit Service, Notification Service, WebSocket Gateway

**Real-Time (WebSocket)**:
- WebSocket Gateway → Browser sessions (push task changes, reminders)

### 1.3 Event Flow — Complete Path for Task Mutation

```
User Action (e.g., complete task)
  │
  ▼
Chat API (FastAPI + MCP)
  ├── 1. Write to PostgreSQL (task.completed = true)
  ├── 2. Publish "task.completed" to Kafka topic "task-events" via Dapr Pub/Sub
  │
  ├──► Recurring Service (subscribes to "task-events")
  │      └── If task has recurrence rule → create next instance via Dapr Service Invocation → API
  │           └── API publishes "task.created" → loop continues
  │
  ├──► Audit Service (subscribes to "task-events")
  │      └── Write ActivityLogEntry to PostgreSQL
  │           └── Publish "audit.entry-created" to "task-updates"
  │
  ├──► Notification Service (subscribes to "task-events")
  │      └── If completed task had pending reminder → cancel it (Dapr Jobs API)
  │
  └──► WebSocket Gateway (subscribes to "task-updates")
         └── Push "sync.task-changed" to all user's connected WebSocket sessions
```

**Spec mapping**: FR-029 (durable events), FR-033 (recurring via completion event), FR-019–023 (audit logging), FR-024–026 (real-time sync), FR-006 (cancel reminder on complete).

---

## 2. Services

### 2.1 Service Inventory

| # | Service | Technology | Role | Dapr Building Blocks | Spec Refs |
|---|---------|-----------|------|---------------------|-----------|
| 1 | **Frontend** | Next.js 14 + TypeScript | Web UI. Renders tasks, filters, activity log. Connects to WebSocket Gateway for real-time push. | None (client-side) | US-1–5, US-7, US-8 |
| 2 | **Chat API** | FastAPI + MCP + Cohere | Core REST API. Task CRUD, auth, search/filter, AI chatbot. Publishes all task events to Kafka. Single source of truth for task mutations. | Pub/Sub, Secrets, State | FR-001–018, FR-027–029 |
| 3 | **Notification Service** | FastAPI (lightweight) | Subscribes to task events to schedule/cancel reminders. Uses Dapr Jobs API for time-triggered reminder delivery. Pushes fired reminders to WebSocket Gateway. | Pub/Sub, Jobs, State | FR-004–006, FR-025, FR-032 |
| 4 | **Recurring Task Service** | FastAPI (lightweight) | Subscribes to task.completed events. When a completed task has a recurrence rule, calculates the next due date and creates the next instance by calling the Chat API via Dapr Service Invocation. | Pub/Sub, Service Invocation | FR-007–009, FR-033 |
| 5 | **Audit Service** | FastAPI (lightweight) | Subscribes to all task and reminder events. Writes immutable activity log entries to PostgreSQL. Publishes audit confirmations to "task-updates" for sync broadcast. | Pub/Sub, Secrets | FR-019–023a |
| 6 | **WebSocket Gateway** | FastAPI + WebSocket | Maintains persistent WebSocket connections per user. Subscribes to "task-updates" and "reminders" topics. Pushes real-time changes and reminder notifications to all active sessions. | Pub/Sub, State | FR-024–026, FR-034 |

### 2.2 Why These Services

| Decision | Justification | Spec Ref |
|----------|---------------|----------|
| Separate Notification Service | Reminder scheduling is a distinct concern (time-triggered jobs) separate from task CRUD | FR-032 "scheduled jobs, not polling" |
| Separate Recurring Service | Recurring task generation must be triggered by completion events, not polling; isolates complex date logic | FR-033 |
| Separate Audit Service | Immutable audit log is a cross-cutting concern consuming events from all sources; independent failure domain | FR-019–023 |
| Separate WebSocket Gateway | Stateful (long-lived connections) vs. stateless API; must scale independently; mixing them creates scaling conflicts | FR-024, FR-034 |
| Chat API as single entry point | All task mutations go through one service to ensure event publishing consistency; Recurring Service calls back to API, not DB directly | FR-029 |

### 2.3 Service Resource Budgets

| Service | Memory Limit | CPU Limit | Replicas (Local) | Replicas (Prod) |
|---------|-------------|-----------|-------------------|-----------------|
| Frontend | 256Mi | 250m | 1 | 2 |
| Chat API | 512Mi | 500m | 1 | 2 |
| Notification Service | 256Mi | 250m | 1 | 1 |
| Recurring Service | 256Mi | 250m | 1 | 1 |
| Audit Service | 256Mi | 250m | 1 | 1 |
| WebSocket Gateway | 256Mi | 250m | 1 | 2 |
| Kafka (single broker) | 512Mi | 500m | 1 | managed |
| PostgreSQL | 512Mi | 500m | 1 | managed |

---

## 3. Kafka Design

### 3.1 Topics

| Topic | Purpose | Partition Key | Retention | Partitions (Local) | Partitions (Prod) |
|-------|---------|---------------|-----------|--------------------|--------------------|
| `task-events` | All task lifecycle events (created, updated, completed, uncompleted, deleted) | `user_id` | 7 days | 3 | 6 |
| `reminders` | Reminder lifecycle events (scheduled, fired, cancelled) | `user_id` | 7 days | 3 | 6 |
| `task-updates` | Aggregated change notifications for real-time sync + audit confirmations | `user_id` | 7 days | 3 | 6 |

**Partitioning rationale**: Partition by `user_id` guarantees per-user event ordering (FR-030). All events for a single user land on the same partition, ensuring consumers process them in the order they were produced.

### 3.2 Event Categories

Per spec "Event Categories" section:

| Category | Events | Topic | Payload |
|----------|--------|-------|---------|
| **Task Events** | task.created, task.updated, task.completed, task.uncompleted, task.deleted | `task-events` | Full task state + changed fields |
| **Reminder Events** | reminder.scheduled, reminder.fired, reminder.cancelled | `reminders` | task_id, user_id, scheduled_time |
| **Recurring Events** | recurrence.triggered, recurrence.instance-created, recurrence.stopped | `task-events` | parent task_id, recurrence pattern, new instance_id |
| **Sync Events** | sync.task-changed | `task-updates` | user_id + changed task state |
| **Audit Events** | audit.entry-created | `task-updates` | Full audit log entry |

### 3.3 Producers & Consumers per Service

| Service | Produces To | Consumes From | Consumer Group |
|---------|------------|---------------|----------------|
| **Chat API** | `task-events` (task.*, recurrence.stopped) | — | — |
| **Notification Service** | `reminders` (reminder.scheduled, .fired, .cancelled) | `task-events` (task.created, .updated, .completed, .deleted) | `notification-svc` |
| **Recurring Service** | — (calls API via Service Invocation, which produces) | `task-events` (task.completed) | `recurring-svc` |
| **Audit Service** | `task-updates` (audit.entry-created) | `task-events` (task.*), `reminders` (reminder.*) | `audit-svc` |
| **WebSocket Gateway** | — | `task-updates` (sync.*, audit.*), `reminders` (reminder.fired) | `websocket-gw` |

### 3.4 Event Payload Schema (CloudEvents v1.0)

All events follow the CloudEvents v1.0 envelope, which is Dapr-native:

```json
{
  "specversion": "1.0",
  "id": "<uuid>",
  "type": "task.completed",
  "source": "pakaura/api",
  "time": "2026-02-09T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "<task_id>",
  "data": {
    "user_id": "<uuid>",
    "task_id": "<uuid>",
    "correlation_id": "<uuid>",
    "payload": { "...event-specific data..." }
  }
}
```

This satisfies the Event Payload Requirements (spec): unique event ID (`id`), event type (`type`), timestamp (`time`), user ID, task ID, payload, correlation ID.

### 3.5 Event Flows per Spec Use Case

**Use Case 1: Task Reminders (FR-004, FR-032)**
```
API sets due_date on task
  → Publishes task.created/task.updated to "task-events"
  → Notification Service receives event
     → Schedules Dapr Job for (due_date - reminder_lead_minutes)
     → Publishes reminder.scheduled to "reminders"
  → When job fires at scheduled time:
     → Notification Service publishes reminder.fired to "reminders"
     → WebSocket Gateway pushes notification to user's sessions
     → Audit Service logs "reminder sent"
```

**Use Case 2: Recurring Tasks (FR-007, FR-033)**
```
User completes recurring task
  → API publishes task.completed to "task-events"
  → Recurring Service receives event, checks recurrence_rule
     → Calculates next due date
     → Calls Chat API via Dapr Service Invocation: POST /api/v1/tasks
     → API creates next instance, publishes task.created
     → Full event pipeline triggers for new instance
```

**Use Case 3: Activity/Audit Log (FR-019, FR-023)**
```
Any task mutation event on "task-events"
  → Audit Service receives event
     → Writes immutable ActivityLogEntry to PostgreSQL
     → Publishes audit.entry-created to "task-updates"
```

**Use Case 4: Real-Time Sync (FR-024, FR-034)**
```
sync.task-changed on "task-updates"
  → WebSocket Gateway receives event
     → Looks up user_id connections in Dapr State Store
     → Pushes JSON payload to all matching WebSocket connections
     → If user reconnects, client sends catchup request
```

### 3.6 Fault Tolerance

| Scenario | Behavior | Spec Ref |
|----------|----------|----------|
| Kafka broker down | Events buffered locally by Dapr sidecar, retried on recovery | FR-031, SC-008 |
| Consumer pod restart | Kafka consumer group rebalances, resumes from last committed offset | FR-043, SC-007 |
| Event processing failure | Dead-letter topic after 3 retries; alert in monitoring | FR-031 |
| Duplicate events | Consumers implement idempotent processing using event ID | FR-030 |

---

## 4. Dapr Components

### 4.1 Component Inventory

| Component Name | Dapr Building Block | Backing Infrastructure | Configuration |
|---------------|--------------------|-----------------------|---------------|
| `pubsub-kafka` | Pub/Sub | Apache Kafka | 3 topics, consumer groups per service, CloudEvents envelope, SASL auth (prod) |
| `statestore-redis` | State Store | Redis (local) / Dapr in-memory | WebSocket session mapping, reminder state cache, TTL-based expiry |
| `secretstore-k8s` | Secrets Store | Kubernetes Secrets | DATABASE_URL, JWT_SECRET, COHERE_API_KEY |
| `jobs-scheduler` | Jobs API | Dapr Jobs (built-in) | One-time triggers for reminders, cron for recurring checks, persists across restarts |

### 4.2 pubsub.kafka — Pub/Sub Component

**Purpose**: Decouple application event publishing/subscribing from Kafka broker details. Application code uses Dapr Pub/Sub API; the underlying Kafka is an infrastructure detail.

**Spec mapping**: FR-029 (durable events via Kafka), FR Infrastructure Abstraction (pub/sub abstraction).

**Configuration (Local)**:
- Broker: `kafka.pakaura.svc.cluster.local:9092`
- No authentication (internal cluster)
- Consumer groups: one per service

**Configuration (Production)**:
- Broker: Oracle Streaming Service endpoint or self-managed Kafka cluster
- SASL/SCRAM authentication
- TLS enabled

**Subscription mapping**:

| Service | Subscribes To | Topic | Dapr Route |
|---------|--------------|-------|------------|
| Recurring Service | `task.completed` | `task-events` | `/events/task-completed` |
| Audit Service | `task.*` | `task-events` | `/events/task-any` |
| Audit Service | `reminder.*` | `reminders` | `/events/reminder-any` |
| Notification Service | `task.created`, `task.updated` | `task-events` | `/events/task-check-reminder` |
| Notification Service | `task.completed`, `task.deleted` | `task-events` | `/events/task-cancel-reminder` |
| WebSocket Gateway | `sync.task-changed`, `audit.*` | `task-updates` | `/events/sync` |
| WebSocket Gateway | `reminder.fired` | `reminders` | `/events/reminder-push` |

### 4.3 State Store

**Purpose**: Fast-access ephemeral state for WebSocket connection mapping and reminder scheduling state. Not critical data — rebuilds on restart.

**Spec mapping**: FR Infrastructure Abstraction (state management abstraction).

| State Key Pattern | Service | Data | TTL |
|-------------------|---------|------|-----|
| `ws:user:{user_id}` | WebSocket Gateway | List of active connection IDs | Session-scoped |
| `reminder:{task_id}` | Notification Service | Dapr job ID, scheduled time, status | Until fired/cancelled |

**Local**: Dapr in-memory state store (simplest, no Redis dependency)
**Production**: Redis via Dapr state store component

### 4.4 Secret Store

**Purpose**: Retrieve all secrets (database credentials, API keys, JWT signing keys) through Dapr's secrets API rather than environment variables. Centralizes secret access and enables rotation without pod restarts.

**Spec mapping**: FR Infrastructure Abstraction (secrets abstraction), FR-042 (Kubernetes secrets for production).

**Secrets managed**:
- `DATABASE_URL` — PostgreSQL connection string
- `JWT_SECRET` — JWT signing key
- `COHERE_API_KEY` — AI model API key
- `KAFKA_SASL_PASSWORD` — Kafka auth (production only)

**Backing store**: Kubernetes Secrets (both local and production). The Dapr `kubernetes` secret store reads from K8s secrets natively.

### 4.5 Jobs / Scheduler

**Purpose**: Schedule reminder notifications at specific times (one-time triggers) and handle recurring task checks. Persists job state across pod restarts.

**Spec mapping**: FR-032 (scheduled jobs, not polling), FR Infrastructure Abstraction (scheduled jobs abstraction).

| Job Type | Trigger | Service | Action |
|----------|---------|---------|--------|
| Reminder | One-time at `(due_date - lead_time)` | Notification Service | Fire reminder event to "reminders" topic |
| Activity pruning | Cron: daily at 02:00 UTC | Audit Service | Delete entries older than 90 days (FR-023a) |

**How it works**:
1. Chat API publishes `task.created`/`task.updated` with `due_date`
2. Notification Service receives event, calculates trigger time
3. Notification Service registers a Dapr Job with the calculated trigger time
4. Dapr Jobs API fires the callback at the scheduled time
5. Notification Service publishes `reminder.fired` to Kafka
6. Job state survives pod restarts (Dapr Jobs persists to its state store)

### 4.6 Service Invocation

**Purpose**: Service-to-service calls with built-in retries, mTLS, and observability. Handles service discovery automatically via Kubernetes DNS.

**Spec mapping**: FR Infrastructure Abstraction (service invocation abstraction).

| Caller | Target | Method | Purpose | Retry Policy |
|--------|--------|--------|---------|-------------|
| Recurring Service | Chat API | `POST /api/v1/tasks` | Create next recurring task instance | 3 retries, exponential backoff |
| Notification Service | WebSocket Gateway | `POST /internal/notify` | Push reminder notification to user sessions | 2 retries |

**Why Service Invocation instead of direct HTTP**: Dapr handles service discovery, automatic retries, mTLS encryption, and distributed tracing — all without application code changes.

---

## 5. Database Schema Evolution

### 5.1 Migration Strategy

A single Alembic migration (`003_phase_v_schema.py`) extends the existing schema. No existing tables are dropped or renamed. Backward compatibility preserved.

### 5.2 Schema Changes

**tasks table — Add columns**:
- `due_date` (TIMESTAMPTZ, nullable) — FR-001
- `reminder_lead_minutes` (INTEGER, nullable, default 30) — FR-005
- `priority` (VARCHAR(10), default 'none', CHECK IN ('none','low','medium','high','urgent')) — FR-010
- `recurrence_rule_id` (UUID, FK to recurrence_rules, nullable) — FR-007
- `recurrence_parent_id` (UUID, FK to tasks, nullable) — links instances to parent

**New indexes on tasks**:
- `idx_tasks_user_due_date` (user_id, due_date) — due date sorting/filtering
- `idx_tasks_user_priority` (user_id, priority) — priority filtering
- `idx_tasks_title_trgm` (GIN trigram index on title) — full-text search (FR-015)

**tags table** (new):
- `id` (UUID, PK), `user_id` (UUID, FK), `name` (VARCHAR(30)), `created_at` (TIMESTAMPTZ)
- UNIQUE constraint on (user_id, lower(name)) — case-insensitive per FR-012

**task_tags table** (new, junction):
- `task_id` (UUID, FK CASCADE), `tag_id` (UUID, FK CASCADE), PK (task_id, tag_id)
- Max 10 tags per task enforced at application level (FR-013)

**recurrence_rules table** (new):
- `id` (UUID, PK), `pattern_type` (VARCHAR(10), CHECK), `interval_days` (INT), `day_of_week` (INT 0–6), `day_of_month` (INT 1–31), `active` (BOOLEAN), `created_at`

**activity_log table** (new):
- `id` (UUID, PK), `user_id` (UUID, FK), `task_id` (UUID, nullable), `action_type` (VARCHAR(30)), `actor` ('user'|'system'), `changed_fields` (JSONB), `created_at` (TIMESTAMPTZ)
- INDEX: `idx_activity_user_created` (user_id, created_at DESC)
- 90-day retention with automatic pruning (FR-023a)

**reminders table** (new):
- `id` (UUID, PK), `task_id` (UUID, FK CASCADE), `user_id` (UUID, FK), `scheduled_at` (TIMESTAMPTZ), `status` ('pending'|'fired'|'cancelled'), `dapr_job_id` (VARCHAR(100)), `created_at`

---

## 6. API Contract Evolution

### 6.1 Extended Endpoints

**`POST /api/v1/tasks`** — extended request body adds: `due_date`, `reminder_lead_minutes`, `priority`, `tags[]`, `recurrence{}`.

**`PATCH /api/v1/tasks/{task_id}`** — extended with same optional fields.

**`GET /api/v1/tasks`** — extended query parameters: `completed`, `priority`, `tag` (repeatable), `due_before`, `due_after`, `overdue`, `search`, `sort`, `order`, `page`, `per_page`.

### 6.2 New Endpoints

| Method | Path | Purpose | Spec Ref |
|--------|------|---------|----------|
| GET | `/api/v1/tags` | List user's tags (auto-complete) | FR-014 |
| GET | `/api/v1/activity` | Paginated activity log | FR-022 |
| GET | `/api/v1/tasks/{id}/activity` | Activity log for specific task | FR-022 |
| DELETE | `/api/v1/tasks/{id}/recurrence` | Stop recurrence | FR-009 |

### 6.3 WebSocket Endpoint

**`WS /ws/{user_id}`** — WebSocket Gateway
- Auth: JWT token as query parameter or first message
- Server pushes: `{ "type": "sync.task-changed|reminder.fired", "data": {...} }`
- Reconnect: client sends `{ "type": "catchup", "since": "ISO8601" }` to receive missed events

### 6.4 Internal Endpoints (Service-to-Service via Dapr)

| Service | Endpoint | Trigger |
|---------|----------|---------|
| Notification | `POST /events/task-check-reminder` | task.created, task.updated |
| Notification | `POST /events/task-cancel-reminder` | task.completed, task.deleted |
| Recurring | `POST /events/task-completed` | task.completed with recurrence_rule |
| Audit | `POST /events/task-any` | all task events |
| Audit | `POST /events/reminder-any` | all reminder events |
| WebSocket GW | `POST /events/sync` | sync.task-changed, audit.* |
| WebSocket GW | `POST /events/reminder-push` | reminder.fired |
| WebSocket GW | `POST /internal/notify` | direct push from Notification Service |

---

## 7. Project Structure

### 7.1 Source Code Layout

```text
api/                                    # Chat API (FastAPI + MCP) — EXTENDED
├── src/
│   ├── models/
│   │   ├── task.py                    # EXTEND — add due_date, priority, recurrence fields
│   │   ├── tag.py                     # NEW — Tag model
│   │   ├── task_tag.py                # NEW — junction table
│   │   ├── recurrence_rule.py         # NEW — RecurrenceRule model
│   │   ├── activity_log.py            # NEW — ActivityLogEntry model
│   │   └── reminder.py                # NEW — Reminder model
│   ├── routes/
│   │   ├── tasks.py                   # EXTEND — search/filter/sort, new fields
│   │   ├── ai.py                      # EXTEND — new chatbot commands (FR-027)
│   │   ├── tags.py                    # NEW — tag CRUD + auto-complete
│   │   └── activity.py                # NEW — activity log read endpoint
│   ├── services/
│   │   ├── task_service.py            # EXTEND — event publishing, new fields
│   │   ├── tag_service.py             # NEW — tag operations
│   │   ├── activity_service.py        # NEW — activity log queries
│   │   └── event_publisher.py         # NEW — Dapr pub/sub publishing helper
│   ├── events/
│   │   └── schemas.py                 # NEW — CloudEvents envelope definitions
│   └── db/migrations/versions/
│       └── 003_phase_v_schema.py      # NEW — all Phase V tables + columns

services/                               # NEW — Event-processing microservices
├── notification/
│   ├── src/
│   │   ├── main.py                    # FastAPI app, Dapr event handlers
│   │   ├── scheduler.py               # Dapr Jobs API integration
│   │   └── handlers.py                # Event subscription handlers
│   ├── Dockerfile
│   └── requirements.txt
├── recurring/
│   ├── src/
│   │   ├── main.py                    # FastAPI app, Dapr event handlers
│   │   ├── generator.py               # Next-instance date calculation
│   │   └── handlers.py                # task.completed handler
│   ├── Dockerfile
│   └── requirements.txt
├── audit/
│   ├── src/
│   │   ├── main.py                    # FastAPI app, Dapr event handlers
│   │   ├── writer.py                  # Activity log DB writer
│   │   └── handlers.py                # Event subscription handlers
│   ├── Dockerfile
│   └── requirements.txt
└── websocket-gateway/
    ├── src/
    │   ├── main.py                    # FastAPI + WebSocket manager
    │   ├── connections.py             # Per-user connection registry (Dapr State)
    │   └── handlers.py                # Dapr event → WebSocket push
    ├── Dockerfile
    └── requirements.txt

frontend/                               # Frontend (Next.js) — EXTENDED
├── src/
│   ├── app/(protected)/
│   │   ├── dashboard/page.tsx         # EXTEND — filters, search, sort, priority/tag UI
│   │   └── activity/page.tsx          # NEW — activity log page
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── TaskItem.tsx           # EXTEND — due date, priority badge, tags, overdue
│   │   │   ├── TaskForm.tsx           # EXTEND — due date picker, priority, tags, recurrence
│   │   │   ├── TaskFilters.tsx        # NEW — search bar, filter dropdowns, sort
│   │   │   └── TaskList.tsx           # EXTEND — integrate filters
│   │   ├── activity/
│   │   │   └── ActivityLog.tsx        # NEW — paginated log display
│   │   └── notifications/
│   │       └── ReminderToast.tsx      # NEW — in-app notification popup
│   ├── hooks/
│   │   ├── useWebSocket.ts            # NEW — WebSocket connection + reconnect
│   │   └── useRealTimeSync.ts         # NEW — sync state from WS events
│   └── lib/
│       ├── api.ts                     # EXTEND — new query params, new endpoints
│       └── websocket.ts               # NEW — WebSocket client utility

infra/                                  # Infrastructure — EXTENDED
├── helm/pakaura/
│   ├── Chart.yaml                     # UPDATE — version 5.0.0
│   ├── values.yaml                    # EXTEND — new services, Kafka, Dapr, monitoring
│   ├── values-local.yaml              # EXTEND — local overrides
│   ├── values-production.yaml         # NEW — Oracle OKE production config
│   ├── templates/
│   │   ├── kafka/                     # NEW — Kafka StatefulSet + Service
│   │   ├── notification/              # NEW — Deployment + Service
│   │   ├── recurring/                 # NEW — Deployment + Service
│   │   ├── audit/                     # NEW — Deployment + Service
│   │   ├── websocket-gateway/         # NEW — Deployment + Service
│   │   ├── dapr/                      # NEW — Dapr component YAMLs
│   │   │   ├── pubsub-kafka.yaml
│   │   │   ├── statestore.yaml
│   │   │   ├── secretstore.yaml
│   │   │   └── subscriptions.yaml
│   │   └── monitoring/                # NEW — Prometheus + Grafana
│   └── templates/_helpers.tpl         # EXTEND — new service label helpers
├── docker/
│   ├── api.Dockerfile                 # existing
│   ├── frontend.Dockerfile            # existing
│   ├── notification.Dockerfile        # NEW
│   ├── recurring.Dockerfile           # NEW
│   ├── audit.Dockerfile               # NEW
│   └── websocket-gateway.Dockerfile   # NEW

.github/
└── workflows/
    └── deploy.yml                     # NEW — CI/CD pipeline
```

---

## 8. Deployment Strategy

### 8.1 Minikube (Local) — FR-035–038

**Prerequisites**: Minikube running, Dapr CLI installed.

**Steps**:
1. Install Dapr on Minikube: `dapr init -k`
2. Build all 6 Docker images locally, load into Minikube: `minikube image load <image>`
3. Deploy: `helm install pakaura infra/helm/pakaura -f infra/helm/pakaura/values-local.yaml -n pakaura --create-namespace`

**Local-specific configuration**:

| Concern | Local Setting | Spec Ref |
|---------|--------------|----------|
| Kafka | Single-broker StatefulSet (Strimzi or plain) | FR-036 |
| PostgreSQL | Single pod with emptyDir (from Phase IV) | FR-036 |
| Secrets | Kubernetes secrets with local dev values | FR-038 |
| Images | `imagePullPolicy: Never` (local builds) | FR-037 |
| HTTPS/TLS | Not required (localhost via port-forward) | spec assumptions |
| Dapr State Store | In-memory (no Redis dependency) | simplification |
| Monitoring | Optional lightweight Prometheus | spec line 492 |
| Replicas | 1 per service | spec line 494 |

**Reproducibility (FR-037)**: Single `helm install` command plus image builds. A `Makefile` or script chains the build and deploy steps.

### 8.2 Cloud Kubernetes (Oracle OKE) — FR-039–043

**Prerequisites**: OKE cluster provisioned, OCIR (Oracle Container Image Registry) configured, Dapr installed on cluster.

**Steps**:
1. Provision OKE cluster via Oracle Cloud Console (or Terraform)
2. Install Dapr: `dapr init -k --runtime-version 1.14`
3. Configure managed services (Oracle Streaming, Autonomous DB) or self-managed equivalents
4. Push Docker images to OCIR
5. Deploy: `helm install pakaura infra/helm/pakaura -f infra/helm/pakaura/values-production.yaml -n pakaura --create-namespace`
6. Configure Ingress controller + TLS certificate for HTTPS (FR-041)

**Production-specific configuration**:

| Concern | Production Setting | Spec Ref |
|---------|-------------------|----------|
| Kafka | Oracle Streaming Service (Kafka-compatible) or 3-broker self-managed | FR-040 |
| PostgreSQL | Oracle Autonomous DB (PG-compatible) or PVC-backed PostgreSQL | FR-040 |
| Secrets | Kubernetes secrets with rotated production values | FR-042 |
| Images | OCIR, `imagePullPolicy: Always` | FR-039 |
| HTTPS/TLS | Required with valid cert (Let's Encrypt or Oracle cert) | FR-041 |
| Domain | Public IP or domain via Ingress | FR-041 |
| Dapr State Store | Redis (managed or pod) | production config |
| Monitoring | Full Prometheus + Grafana + Loki stack | FR-048–051 |
| Replicas | Configurable (2 for API, Frontend, WebSocket GW) | spec line 494 |

### 8.3 Helm Chart Reuse from Phase IV

**Evolution strategy**: The existing Phase IV Helm chart (`infra/helm/pakaura/`) is extended, not replaced.

**What stays the same**:
- `Chart.yaml` structure (version bumped to 5.0.0)
- `templates/namespace.yaml`
- `templates/secrets.yaml` (extended with new secrets)
- `templates/configmap.yaml` (extended with new configs)
- `templates/api/` (extended with Dapr annotations)
- `templates/frontend/` (unchanged)
- `templates/postgres/` (unchanged)
- `templates/_helpers.tpl` (extended with new labels)
- `values-local.yaml` pattern (extended)

**What is added**:
- `values-production.yaml` (new)
- `templates/kafka/` (new)
- `templates/notification/`, `recurring/`, `audit/`, `websocket-gateway/` (new)
- `templates/dapr/` (new — component YAMLs)
- `templates/monitoring/` (new)

**Values layering**:
```
values.yaml (shared defaults for all services)
  └── values-local.yaml (Minikube: imagePullPolicy=Never, single Kafka, emptyDir PG, 1 replica)
  └── values-production.yaml (OKE: imagePullPolicy=Always, managed services, TLS, multi-replica)
```

### 8.4 Fallback Cloud Providers

Per spec assumption: if Oracle OKE free tier is insufficient, equivalent deployment on:
- **Azure AKS**: Replace OCIR with ACR, Oracle Streaming with Azure Event Hubs (Kafka-compatible)
- **Google GKE**: Replace OCIR with Artifact Registry, Oracle Streaming with Confluent Cloud or self-managed Kafka

The Helm chart and Dapr abstraction make provider switching a `values-production.yaml` change, not a code change.

---

## 9. CI/CD — FR-044–047

### 9.1 GitHub Actions Pipeline: `.github/workflows/deploy.yml`

**Trigger**: Push to `main` branch (FR-045). Feature branches trigger Stage 1 + Stage 2 only (build + test, no deploy) per spec assumption.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline Stages                         │
│                                                                 │
│  Stage 1: TEST                                                  │
│  ├── pytest api/                                                │
│  ├── pytest services/notification/                              │
│  ├── pytest services/recurring/                                 │
│  ├── pytest services/audit/                                     │
│  ├── pytest services/websocket-gateway/                         │
│  └── npm test (frontend)                                        │
│  Gate: All tests must pass (FR-046)                             │
│                                                                 │
│  Stage 2: BUILD                                                 │
│  ├── Build 6 Docker images (api, frontend, 4 services)         │
│  ├── Tag with git SHA + "latest"                                │
│  └── Push to OCIR (Oracle Container Image Registry)             │
│  Gate: All images built and pushed                              │
│                                                                 │
│  Stage 3: DEPLOY (main branch only)                             │
│  ├── Configure kubectl for OKE cluster (kubeconfig from secret) │
│  ├── helm upgrade --install pakaura ... -f values-production    │
│  └── kubectl rollout status (wait for all deployments)          │
│                                                                 │
│  Stage 4: VERIFY                                                │
│  ├── Health check: curl production URL                          │
│  └── Smoke test: register + create task + verify API response   │
│                                                                 │
│  Target: Complete in <15 minutes (SC-009)                       │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Pipeline Secrets (GitHub Actions Encrypted Secrets)

| Secret | Purpose |
|--------|---------|
| `OKE_KUBECONFIG` | Kubernetes cluster access |
| `OCIR_USERNAME` | Container registry auth |
| `OCIR_PASSWORD` | Container registry auth |
| `DATABASE_URL` | Production PostgreSQL URL |
| `JWT_SECRET` | JWT signing key |
| `COHERE_API_KEY` | AI model API key |
| `KAFKA_SASL_PASSWORD` | Kafka auth (if applicable) |

### 9.3 Rollback Strategy (FR-047)

- **Helm-based**: `helm rollback pakaura <revision> -n pakaura`
- **Triggered via**: GitHub Actions `workflow_dispatch` with revision number input
- **Helm history**: Each deploy creates a new revision; `helm history pakaura` shows all versions
- **Database**: Alembic `downgrade` for schema rollback (run manually as safety measure)

### 9.4 Feature Branch Behavior

Feature branches (not `main`) trigger:
- Stage 1 (Test) — always
- Stage 2 (Build) — always (validates Docker builds)
- Stage 3 (Deploy) — **skipped** (per spec assumption)
- Stage 4 (Verify) — **skipped**

---

## 10. Monitoring & Observability — FR-048–051

### 10.1 Stack

| Component | Purpose | Deployment |
|-----------|---------|------------|
| **Prometheus** | Metrics scraping and storage | Helm subchart in `templates/monitoring/` |
| **Grafana** | Dashboard visualization (FR-051) | Helm subchart with pre-configured dashboards |
| **Loki** | Log aggregation (FR-048) | Lightweight log store, Grafana datasource |
| **Promtail** | Log shipping from pods to Loki | DaemonSet on all nodes |

### 10.2 Structured Logging (FR-048)

All services emit JSON-structured logs:
```json
{
  "timestamp": "2026-02-09T10:30:00Z",
  "level": "INFO",
  "service": "api",
  "message": "Task completed",
  "task_id": "uuid",
  "user_id": "uuid",
  "correlation_id": "uuid"
}
```

### 10.3 Metrics (FR-050)

| Metric | Source | Type | Dashboard Panel |
|--------|--------|------|-----------------|
| `http_requests_total` | API, all services | Counter | Request rate |
| `http_request_duration_seconds` | API, all services | Histogram | p50, p95, p99 latency |
| `http_responses_by_status` | API, all services | Counter | Error rate |
| `kafka_consumer_lag` | Kafka exporters | Gauge | Consumer lag (SC-011) |
| `websocket_active_connections` | WebSocket Gateway | Gauge | Active WS connections |
| `events_published_total` | API | Counter | Event throughput |
| `events_processed_total` | All consumers | Counter | Processing throughput |
| `reminder_delivery_latency_seconds` | Notification Service | Histogram | Reminder delivery (SC-002) |

### 10.4 Health Checks (FR-049)

Every service exposes:
- `GET /health/ready` — readiness probe (checks dependencies: DB, Kafka, Dapr sidecar)
- `GET /health/live` — liveness probe (process running, not deadlocked)

Kubernetes uses these for automated pod restart (liveness) and traffic routing (readiness).

### 10.5 Grafana Dashboards (FR-051)

Pre-configured dashboards:
1. **System Overview**: All service request rates, error rates, latency
2. **Kafka Events**: Topic throughput, consumer lag per group, partition distribution
3. **WebSocket**: Active connections, message push rate
4. **Reminders**: Scheduling rate, delivery latency, cancellation rate

---

## 11. Key Design Decisions

| # | Decision | Rationale | Alternatives Rejected |
|---|----------|-----------|----------------------|
| 1 | CloudEvents v1.0 envelope for all Kafka events | Standard format, Dapr-native support, ensures correlation_id and tracing | Custom JSON — no standard, harder to trace |
| 2 | Partition Kafka topics by user_id | Guarantees per-user event ordering (FR-030) | Random partitioning — breaks ordering guarantee |
| 3 | Separate WebSocket Gateway service | Stateful (long-lived connections) vs stateless API; independent scaling | WebSocket in API — mixes stateful/stateless concerns |
| 4 | Recurring Service calls API via Service Invocation | Ensures task creation goes through same validation and event publishing path | Direct DB write — bypasses event pipeline, violates DRY |
| 5 | In-memory/Redis for Dapr State Store | WebSocket connection mapping needs fast lookup; ephemeral data rebuilds on restart | PostgreSQL state — unnecessary latency for non-critical data |
| 6 | Activity log in PostgreSQL (not Kafka-only) | 90-day retention with SQL queries, pagination, per-task filtering; Kafka is 7-day transport only | Kafka as permanent store — hard to query, no pagination |
| 7 | Strimzi operator for Kafka on Minikube | Production-like Kafka management; operator handles broker lifecycle | Plain Docker Kafka — no persistence config, harder to manage |
| 8 | Dapr as abstraction layer | Constitution-mandated infrastructure abstraction; provides all 5 required building blocks in one runtime | Custom abstractions — more code to maintain, no community support |

---

## 12. Complexity Tracking

No constitution violations. All complexity justified by spec requirements:

| New Complexity | Justification | Would Not Exist Without |
|---------------|---------------|-------------------------|
| 4 new microservices | Event-driven architecture requires separate consumers for distinct concerns | FR-029–034, Constitution Phase V |
| Kafka infrastructure | Constitution mandates Kafka for all 4 event use cases | Constitution Phase V |
| Dapr sidecar per service | Spec requires abstraction for pub/sub, state, secrets, jobs, invocation | FR Infrastructure Abstraction requirements |
| WebSocket Gateway | Real-time sync requires persistent connections, separate from stateless API | FR-024–026, FR-034 |
| CI/CD pipeline | Production cloud deployment requires automated build/test/deploy | FR-044–047 |
| Monitoring stack | Distributed system requires centralized observability | FR-048–051 |

---

## 13. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Kafka adds operational complexity to local dev | High | Medium | Single-broker on Minikube; Dapr abstracts broker details; clear setup docs |
| Oracle OKE free tier resource limits insufficient | Medium | High | Conservative pod sizing; Azure AKS/GKE as fallback; monitor usage |
| WebSocket blocked by proxies/firewalls | Medium | Medium | Automatic fallback to SSE or long-polling if WS fails |
| Event ordering across Kafka partitions | Medium | Medium | Partition by user_id ensures per-user ordering |
| Dapr sidecar startup latency | Medium | Low | Configure appropriate init delays in health probes |
| CI/CD secrets exposure | Low | High | GitHub encrypted secrets; never commit credentials |

---

## 14. Post-Design Constitution Re-Check

| Gate | Status |
|------|--------|
| I. Spec-Driven | PASS — plan traces every decision to spec FRs |
| II. Single Repo | PASS — all services in same repo under `services/` |
| III. Evolution | PASS — extends existing api/, frontend/, infra/ |
| IV. Single Source | PASS — spec.md remains authoritative |
| V. Clean Architecture | PASS — clear separation: api/, services/, frontend/, infra/ |
| VI. Quality Bar | PASS — no unnecessary abstractions; each service has clear purpose |
| Phase V: Kafka | PASS — 3 topics cover all 4 mandated use cases |
| Phase V: Reliability | PASS — 7-day Kafka retention, PG permanent store, Dapr Jobs persist |

---

## Follow-ups & Risks

1. **Dapr version pinning**: Pin Dapr runtime version (1.14+) across local and production to avoid compatibility issues.
2. **Oracle OKE provisioning**: Requires Oracle Cloud account setup before production deployment can be tested. Start early.
3. **Kafka topic creation**: Decide whether topics are auto-created by Dapr or pre-created via Helm job. Recommend pre-creation for control.
