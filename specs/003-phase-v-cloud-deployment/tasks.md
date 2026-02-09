# Task List: Phase V – Advanced Cloud Deployment

**Branch**: `003-phase-v-cloud-deployment` | **Date**: 2026-02-09
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Rule**: Each task does ONE thing. No implementation — definition only.

---

## Category 1: Kafka Setup (Local & Cloud)

### T-001: Create Kafka StatefulSet Helm template for Minikube

- **Description**: Create a Helm template that deploys a single-broker Kafka instance (Strimzi or plain StatefulSet) with ZooKeeper into the pakaura namespace. Include a Service for internal cluster access on port 9092.
- **Spec refs**: FR-036 (local deployment includes Kafka single-node)
- **Plan refs**: Plan §3.1 (Topics), Plan §8.1 (Minikube local)
- **Preconditions**: Existing Helm chart at `infra/helm/pakaura/` from Phase IV
- **Expected output**: Kafka pod running in Minikube; `kubectl get pods -n pakaura` shows `kafka-0` in Running state; port 9092 accessible within cluster
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/kafka/statefulset.yaml` (NEW)
  - `infra/helm/pakaura/templates/kafka/service.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — add `kafka` section)
  - `infra/helm/pakaura/values-local.yaml` (EXTEND — add local Kafka overrides)

---

### T-002: Create Kafka topics via Helm job

- **Description**: Create a Kubernetes Job (Helm template) that runs after Kafka is ready and creates the three topics: `task-events`, `reminders`, `task-updates`. Each topic has 3 partitions (local) with 7-day retention. Partitioned by `user_id` at the producer level.
- **Spec refs**: FR-029 (durable events), FR-030 (7-day retention), Event Categories section
- **Plan refs**: Plan §3.1 (Topics table)
- **Preconditions**: T-001 (Kafka running)
- **Expected output**: `kafka-topics --list` returns all 3 topics; `kafka-topics --describe` shows 3 partitions each with `retention.ms=604800000`
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/kafka/topic-init-job.yaml` (NEW)

---

### T-003: Add Kafka production configuration to values-production.yaml

- **Description**: Create `values-production.yaml` with Kafka configuration pointing to Oracle Streaming Service (Kafka-compatible) or a managed multi-broker Kafka. Include SASL/SCRAM authentication, TLS, and 6-partition topic configuration.
- **Spec refs**: FR-040 (managed Kafka in production)
- **Plan refs**: Plan §8.2 (Cloud Kubernetes), Plan §4.2 (pubsub-kafka production config)
- **Preconditions**: T-001, T-002 (local Kafka working)
- **Expected output**: `values-production.yaml` exists with Kafka broker endpoints, auth credentials reference, TLS enabled, 6 partitions
- **Files to modify/create**:
  - `infra/helm/pakaura/values-production.yaml` (NEW)

---

## Category 2: Dapr Installation on Kubernetes

### T-004: Document and validate Dapr installation on Minikube

- **Description**: Install Dapr runtime on the local Minikube cluster using `dapr init -k`. Verify Dapr system pods are running in `dapr-system` namespace. Pin to Dapr runtime version 1.14+.
- **Spec refs**: FR-036 (local deployment includes abstraction layer sidecars)
- **Plan refs**: Plan §8.1 step 1 (Install Dapr on Minikube)
- **Preconditions**: Minikube running
- **Expected output**: `kubectl get pods -n dapr-system` shows `dapr-operator`, `dapr-sidecar-injector`, `dapr-placement`, `dapr-scheduler` all Running
- **Files to modify/create**:
  - None (CLI operation; documented in README)

---

### T-005: Document and validate Dapr installation on OKE

- **Description**: Install Dapr runtime on the Oracle OKE cluster using `dapr init -k --runtime-version 1.14`. Verify Dapr system pods are running. Configure for production (mTLS enabled, high availability mode).
- **Spec refs**: FR-039 (deploy to OKE)
- **Plan refs**: Plan §8.2 step 2 (Install Dapr on OKE)
- **Preconditions**: OKE cluster provisioned and kubectl configured
- **Expected output**: `kubectl get pods -n dapr-system` on OKE shows all Dapr system pods Running
- **Files to modify/create**:
  - None (CLI operation; documented in README)

---

## Category 3: Dapr Components Configuration

### T-006: Create Dapr pubsub-kafka component YAML

- **Description**: Create the Dapr Pub/Sub component definition that binds to the Kafka broker. Use `pubsub.kafka` component type with broker address from Helm values. CloudEvents format enabled. Consumer groups per service.
- **Spec refs**: FR-029 (pub/sub abstraction), Infrastructure Abstraction Requirements (Pub/Sub Abstraction)
- **Plan refs**: Plan §4.1 (Component Inventory — pubsub-kafka), Plan §4.2 (pubsub.kafka details)
- **Preconditions**: T-001 (Kafka running), T-004 (Dapr installed)
- **Expected output**: `kubectl get components -n pakaura` shows `pubsub-kafka` component; Dapr dashboard shows component healthy
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/dapr/pubsub-kafka.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — add `dapr.pubsub` config section)

---

### T-007: Create Dapr state store component YAML

- **Description**: Create the Dapr State Store component definition. Local: in-memory state store. Production: Redis-backed state store. Used by WebSocket Gateway (connection mapping) and Notification Service (reminder state).
- **Spec refs**: Infrastructure Abstraction Requirements (State Management Abstraction)
- **Plan refs**: Plan §4.1 (statestore-redis), Plan §4.3 (State Store details)
- **Preconditions**: T-004 (Dapr installed)
- **Expected output**: `kubectl get components -n pakaura` shows `statestore` component
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/dapr/statestore.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — add `dapr.statestore` config section)
  - `infra/helm/pakaura/values-local.yaml` (EXTEND — in-memory override)
  - `infra/helm/pakaura/values-production.yaml` (EXTEND — Redis config)

---

### T-008: Create Dapr secret store component YAML

- **Description**: Create the Dapr Secrets Store component definition backed by Kubernetes Secrets. Services retrieve DATABASE_URL, JWT_SECRET, COHERE_API_KEY, and KAFKA_SASL_PASSWORD through Dapr secrets API.
- **Spec refs**: FR-042 (K8s secrets in production), Infrastructure Abstraction Requirements (Secrets Abstraction)
- **Plan refs**: Plan §4.1 (secretstore-k8s), Plan §4.4 (Secret Store details)
- **Preconditions**: T-004 (Dapr installed), existing `secrets.yaml` from Phase IV
- **Expected output**: `kubectl get components -n pakaura` shows `secretstore-k8s` component; Dapr can read secrets from K8s secrets
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/dapr/secretstore.yaml` (NEW)
  - `infra/helm/pakaura/templates/secrets.yaml` (EXTEND — add new secret keys)

---

### T-009: Create Dapr subscription definitions YAML

- **Description**: Create the declarative Dapr subscription definitions that route events from Kafka topics to specific service endpoints. Map all subscription routes from the plan's subscription table.
- **Spec refs**: FR-029–034 (event architecture), Event Categories section
- **Plan refs**: Plan §4.2 (Subscription mapping table — all 7 subscriptions)
- **Preconditions**: T-006 (pubsub-kafka component exists)
- **Expected output**: `kubectl get subscriptions -n pakaura` shows all subscriptions; each service receives events at its configured route
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/dapr/subscriptions.yaml` (NEW)

---

## Category 4: Backend Event Publishing

### T-010: Create CloudEvents schema definitions module

- **Description**: Create a Python module defining the CloudEvents v1.0 envelope structure and factory functions for each event type (task.created, task.updated, task.completed, task.uncompleted, task.deleted, recurrence.stopped). Each event includes: id, type, source, time, subject, data (user_id, task_id, correlation_id, payload).
- **Spec refs**: Event Payload Requirements (unique ID, type, timestamp, user_id, task_id, payload, correlation_id)
- **Plan refs**: Plan §3.4 (Event Payload Schema)
- **Preconditions**: None
- **Expected output**: Importable module with Pydantic models for each event type; unit tests validating schema compliance
- **Files to modify/create**:
  - `api/src/events/__init__.py` (NEW)
  - `api/src/events/schemas.py` (NEW)

---

### T-011: Create Dapr pub/sub event publisher helper

- **Description**: Create a service helper that publishes events to Kafka via the Dapr HTTP Pub/Sub API. Accepts a CloudEvents envelope and publishes to the specified topic. Includes local buffering/retry when Dapr sidecar is unavailable.
- **Spec refs**: FR-029 (all mutations produce durable event), FR-031 (tolerate unavailability with buffering)
- **Plan refs**: Plan §4.2 (pubsub.kafka), Plan §3.6 (Fault Tolerance)
- **Preconditions**: T-010 (CloudEvents schemas)
- **Expected output**: `event_publisher.publish(topic, event)` sends event via Dapr; retries on failure; unit tests with mocked Dapr API
- **Files to modify/create**:
  - `api/src/services/event_publisher.py` (NEW)

---

### T-012: Integrate event publishing into task CRUD operations

- **Description**: Extend the existing task service to publish a CloudEvent to the `task-events` topic after every task mutation (create, update, complete, uncomplete, delete). Each event carries the full task state and changed fields. Use correlation_id for tracing.
- **Spec refs**: FR-029 (all task mutations produce durable event)
- **Plan refs**: Plan §1.3 (Event Flow — step 2), Plan §3.3 (Chat API produces to task-events)
- **Preconditions**: T-010, T-011 (schemas + publisher)
- **Expected output**: Every task API call produces a corresponding event on `task-events` topic; testable via Kafka console consumer or Dapr logs
- **Files to modify/create**:
  - `api/src/services/task_service.py` (EXTEND)
  - `api/src/routes/tasks.py` (EXTEND — ensure service layer called)

---

## Category 5: Database Schema Evolution

### T-013: Create Alembic migration for Phase V schema

- **Description**: Create a single Alembic migration (`003_phase_v_schema.py`) that adds all Phase V database changes: new columns on tasks table (due_date, reminder_lead_minutes, priority, recurrence_rule_id, recurrence_parent_id), new tables (tags, task_tags, recurrence_rules, activity_log, reminders), and new indexes.
- **Spec refs**: FR-001 (due_date), FR-005 (reminder_lead), FR-010 (priority), FR-007 (recurrence), FR-012 (tags), FR-013 (task_tags), FR-019–023 (activity_log), FR-004 (reminders), Key Entities section
- **Plan refs**: Plan §5.1 (Migration Strategy), Plan §5.2 (Schema Changes — all tables)
- **Preconditions**: Existing Alembic setup from Phase II
- **Expected output**: `alembic upgrade head` succeeds; all new tables exist; `\dt` in psql shows tags, task_tags, recurrence_rules, activity_log, reminders; tasks table has new columns
- **Files to modify/create**:
  - `api/src/db/migrations/versions/003_phase_v_schema.py` (NEW)

---

### T-014: Create SQLAlchemy models for new Phase V entities

- **Description**: Create SQLAlchemy ORM models for: Tag, TaskTag (junction), RecurrenceRule, ActivityLogEntry, Reminder. Extend the existing Task model with new columns (due_date, reminder_lead_minutes, priority, recurrence_rule_id, recurrence_parent_id). Register all models in `__init__.py`.
- **Spec refs**: Key Entities section (Task extended, Tag, Recurrence Rule, Activity Log Entry, Reminder)
- **Plan refs**: Plan §5.2 (Schema Changes — all entity definitions), Plan §7.1 (api/src/models/ layout)
- **Preconditions**: T-013 (migration exists to match)
- **Expected output**: All models importable from `api.src.models`; relationships defined (Task ↔ Tags M2M, Task → RecurrenceRule FK, Task → Reminders)
- **Files to modify/create**:
  - `api/src/models/task.py` (EXTEND)
  - `api/src/models/tag.py` (NEW)
  - `api/src/models/task_tag.py` (NEW)
  - `api/src/models/recurrence_rule.py` (NEW)
  - `api/src/models/activity_log.py` (NEW)
  - `api/src/models/reminder.py` (NEW)
  - `api/src/models/__init__.py` (EXTEND — register new models)

---

## Category 6: Advanced Task API Features

### T-015: Extend task creation endpoint with due date, priority, and recurrence

- **Description**: Extend `POST /api/v1/tasks` to accept optional `due_date` (ISO8601), `reminder_lead_minutes` (int, default 30), `priority` (enum), and `recurrence` (object with pattern, interval_days, day_of_week, day_of_month). Validate all inputs. Create RecurrenceRule record when recurrence is provided.
- **Spec refs**: FR-001 (due date), FR-005 (reminder lead time), FR-007 (recurrence patterns), FR-010 (priority levels)
- **Plan refs**: Plan §6.1 (POST /api/v1/tasks extended body)
- **Preconditions**: T-013, T-014 (schema + models)
- **Expected output**: Task created with all new fields; response includes due_date, priority, recurrence info; invalid inputs return 422
- **Files to modify/create**:
  - `api/src/routes/tasks.py` (EXTEND)
  - `api/src/services/task_service.py` (EXTEND)

---

### T-016: Extend task update endpoint with due date, priority, and recurrence changes

- **Description**: Extend `PATCH /api/v1/tasks/{task_id}` to accept optional changes to `due_date`, `reminder_lead_minutes`, `priority`, and `recurrence`. Track changed fields (old vs new values) for audit events.
- **Spec refs**: FR-002 (clear/change due date), FR-011 (change/remove priority), FR-009 (stop recurrence)
- **Plan refs**: Plan §6.1 (PATCH /api/v1/tasks extended body)
- **Preconditions**: T-015 (creation works first)
- **Expected output**: Task updated with new field values; changed_fields dict available for event publishing; invalid inputs return 422
- **Files to modify/create**:
  - `api/src/routes/tasks.py` (EXTEND)
  - `api/src/services/task_service.py` (EXTEND)

---

### T-017: Create tag management endpoints

- **Description**: Create `GET /api/v1/tags` endpoint returning the user's tags (for auto-complete). Extend task create/update to accept `tags[]` array. Create Tag and TaskTag records. Enforce max 10 tags per task and tag name validation (1–30 chars, alphanumeric + hyphens, case-insensitive stored lowercase).
- **Spec refs**: FR-012 (user-scoped tags), FR-013 (max 10 per task), FR-014 (auto-complete)
- **Plan refs**: Plan §6.2 (GET /api/v1/tags), Plan §5.2 (tags table, task_tags table)
- **Preconditions**: T-013, T-014 (schema + models)
- **Expected output**: Tags CRUD works; auto-complete returns matching tags; 422 on validation failures; max 10 enforced
- **Files to modify/create**:
  - `api/src/routes/tags.py` (NEW)
  - `api/src/services/tag_service.py` (NEW)
  - `api/src/routes/__init__.py` (EXTEND — mount tags router)

---

### T-018: Extend task list endpoint with search, filter, and sort

- **Description**: Extend `GET /api/v1/tasks` with query parameters: `search` (title keyword), `completed` (bool), `priority` (enum), `tag` (repeatable), `due_before`/`due_after` (ISO8601), `overdue` (bool), `sort` (due_date|priority|created_at|title), `order` (asc|desc), `page`, `per_page`. Apply AND logic between search and filters.
- **Spec refs**: FR-015 (full-text search), FR-016 (filters), FR-017 (sort), FR-018 (AND logic)
- **Plan refs**: Plan §6.1 (GET /api/v1/tasks extended query params)
- **Preconditions**: T-013 (indexes: trigram for search, user_due_date, user_priority)
- **Expected output**: Filtering returns correct subsets; sorting orders correctly; search finds matching titles; pagination works; <2s for 500 tasks (SC-004)
- **Files to modify/create**:
  - `api/src/routes/tasks.py` (EXTEND)
  - `api/src/services/task_service.py` (EXTEND)

---

### T-019: Create stop-recurrence endpoint

- **Description**: Create `DELETE /api/v1/tasks/{task_id}/recurrence` endpoint that sets the recurrence rule's `active` flag to false without deleting the task or existing instances. Publishes `recurrence.stopped` event.
- **Spec refs**: FR-009 (stop recurrence without deleting instances)
- **Plan refs**: Plan §6.2 (DELETE /api/v1/tasks/{id}/recurrence)
- **Preconditions**: T-015 (recurrence creation)
- **Expected output**: Recurrence deactivated; no new instances generated on future completions; existing instances unchanged; event published
- **Files to modify/create**:
  - `api/src/routes/tasks.py` (EXTEND)
  - `api/src/services/task_service.py` (EXTEND)

---

## Category 7: Reminder Service

### T-020: Create Notification Service project scaffold

- **Description**: Create the Notification Service project structure: `services/notification/` with `src/main.py` (FastAPI app), `src/handlers.py`, `src/scheduler.py`, `Dockerfile`, `requirements.txt`. Include health check endpoints (`/health/ready`, `/health/live`) and Dapr app-id annotation.
- **Spec refs**: FR-049 (health checks), FR-004 (reminder delivery)
- **Plan refs**: Plan §2.1 (Notification Service), Plan §7.1 (services/notification/ layout)
- **Preconditions**: None
- **Expected output**: Service starts, health endpoints return 200; Docker image builds successfully
- **Files to modify/create**:
  - `services/notification/src/__init__.py` (NEW)
  - `services/notification/src/main.py` (NEW)
  - `services/notification/src/handlers.py` (NEW)
  - `services/notification/src/scheduler.py` (NEW)
  - `services/notification/Dockerfile` (NEW)
  - `services/notification/requirements.txt` (NEW)

---

### T-021: Implement reminder scheduling via Dapr Jobs API

- **Description**: In the Notification Service, implement the handler for `task.created` and `task.updated` events. When a task has a `due_date` and `reminder_lead_minutes`, calculate the trigger time `(due_date - lead_time)` and register a one-time Dapr Job. Store the job reference in Dapr State Store.
- **Spec refs**: FR-004 (send reminder before due date), FR-005 (configurable lead time), FR-032 (scheduled jobs, not polling)
- **Plan refs**: Plan §4.5 (Jobs/Scheduler — how it works steps 1–3), Plan §3.5 (Use Case 1: Task Reminders)
- **Preconditions**: T-020 (service scaffold), T-006 (Dapr pubsub), T-007 (Dapr state store)
- **Expected output**: Dapr Job registered with correct trigger time; state store contains reminder entry; testable by setting a due date and observing job registration
- **Files to modify/create**:
  - `services/notification/src/handlers.py` (EXTEND)
  - `services/notification/src/scheduler.py` (EXTEND)

---

### T-022: Implement reminder cancellation on task complete/delete

- **Description**: In the Notification Service, implement the handler for `task.completed` and `task.deleted` events. When received, look up any pending reminder for that task in the Dapr State Store and cancel the Dapr Job. Publish `reminder.cancelled` event to `reminders` topic.
- **Spec refs**: FR-006 (cancel pending reminders on complete/delete)
- **Plan refs**: Plan §4.2 (Notification subscribes to task-cancel-reminder), Plan §3.5 (Use Case 1 — cancel flow)
- **Preconditions**: T-021 (scheduling works first)
- **Expected output**: Completing or deleting a task with a pending reminder cancels the job; no reminder fires after cancellation; `reminder.cancelled` event published
- **Files to modify/create**:
  - `services/notification/src/handlers.py` (EXTEND)

---

### T-023: Implement reminder firing and notification push

- **Description**: In the Notification Service, implement the Dapr Job callback that fires when a reminder's scheduled time arrives. Publish `reminder.fired` event to the `reminders` topic. Call WebSocket Gateway via Dapr Service Invocation (`POST /internal/notify`) to push the notification to the user's active sessions.
- **Spec refs**: FR-004 (in-app reminder), FR-025 (push to all sessions), SC-002 (<60s delivery)
- **Plan refs**: Plan §4.5 (Jobs — steps 4–5), Plan §4.6 (Service Invocation — Notification→WS Gateway)
- **Preconditions**: T-021, T-022 (scheduling and cancellation)
- **Expected output**: When job fires, reminder.fired event published; WebSocket Gateway receives notification; user sees in-app notification within 60 seconds of scheduled time
- **Files to modify/create**:
  - `services/notification/src/scheduler.py` (EXTEND)
  - `services/notification/src/handlers.py` (EXTEND)

---

### T-024: Create Notification Service Dockerfile and Helm templates

- **Description**: Create the Dockerfile for the Notification Service and the Helm Deployment + Service templates. Include Dapr annotations (app-id: `notification-service`, app-port, protocol). Configure resource limits (256Mi/250m).
- **Spec refs**: FR-036 (all services in local deployment)
- **Plan refs**: Plan §2.3 (Resource Budgets), Plan §7.1 (infra/docker/ and templates/notification/)
- **Preconditions**: T-020 (service scaffold)
- **Expected output**: `docker build` succeeds; Helm template renders valid YAML; pod deploys with Dapr sidecar injected
- **Files to modify/create**:
  - `infra/docker/notification.Dockerfile` (NEW)
  - `infra/helm/pakaura/templates/notification/deployment.yaml` (NEW)
  - `infra/helm/pakaura/templates/notification/service.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — add notification section)

---

## Category 8: Recurring Task Engine

### T-025: Create Recurring Service project scaffold

- **Description**: Create the Recurring Service project structure: `services/recurring/` with `src/main.py` (FastAPI app), `src/handlers.py`, `src/generator.py`, `Dockerfile`, `requirements.txt`. Include health check endpoints and Dapr app-id annotation.
- **Spec refs**: FR-049 (health checks), FR-007–009 (recurring tasks)
- **Plan refs**: Plan §2.1 (Recurring Task Service), Plan §7.1 (services/recurring/ layout)
- **Preconditions**: None
- **Expected output**: Service starts, health endpoints return 200; Docker image builds successfully
- **Files to modify/create**:
  - `services/recurring/src/__init__.py` (NEW)
  - `services/recurring/src/main.py` (NEW)
  - `services/recurring/src/handlers.py` (NEW)
  - `services/recurring/src/generator.py` (NEW)
  - `services/recurring/Dockerfile` (NEW)
  - `services/recurring/requirements.txt` (NEW)

---

### T-026: Implement next-instance date calculation logic

- **Description**: Implement the `generator.py` module with a function that calculates the next due date given a recurrence rule (daily, weekly/day-of-week, monthly/day-of-month, custom/N-days) and the current due date. Handle edge cases: Feb 30 → rolls to March, past dates → next future occurrence.
- **Spec refs**: FR-007 (recurrence patterns: daily, weekly, monthly, custom), Edge Cases (nonexistent dates roll forward, past start dates skip to future)
- **Plan refs**: Plan §3.5 (Use Case 2 — calculates next due date)
- **Preconditions**: T-025 (service scaffold)
- **Expected output**: Unit tests pass for all 4 recurrence patterns + edge cases; pure function, no side effects
- **Files to modify/create**:
  - `services/recurring/src/generator.py` (EXTEND)

---

### T-027: Implement task.completed event handler for recurring generation

- **Description**: In the Recurring Service, implement the handler for `task.completed` events. When the completed task has a `recurrence_rule` that is active, use the generator to calculate the next due date, then call the Chat API via Dapr Service Invocation (`POST /api/v1/tasks`) to create the next instance with `recurrence_parent_id` set.
- **Spec refs**: FR-008 (auto-generate next instance on complete), FR-033 (triggered by completion event, not polling)
- **Plan refs**: Plan §3.5 (Use Case 2 — full flow), Plan §4.6 (Service Invocation — Recurring→API)
- **Preconditions**: T-025, T-026 (scaffold + generator), T-012 (API publishes events)
- **Expected output**: Completing a recurring task creates a new task instance with the next due date; new instance appears in task list within 5 seconds (SC-003)
- **Files to modify/create**:
  - `services/recurring/src/handlers.py` (EXTEND)

---

### T-028: Create Recurring Service Dockerfile and Helm templates

- **Description**: Create the Dockerfile for the Recurring Service and the Helm Deployment + Service templates. Include Dapr annotations (app-id: `recurring-service`, app-port, protocol). Configure resource limits (256Mi/250m).
- **Spec refs**: FR-036 (all services in local deployment)
- **Plan refs**: Plan §2.3 (Resource Budgets), Plan §7.1 (infra layout)
- **Preconditions**: T-025 (service scaffold)
- **Expected output**: `docker build` succeeds; Helm template renders valid YAML; pod deploys with Dapr sidecar injected
- **Files to modify/create**:
  - `infra/docker/recurring.Dockerfile` (NEW)
  - `infra/helm/pakaura/templates/recurring/deployment.yaml` (NEW)
  - `infra/helm/pakaura/templates/recurring/service.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — add recurring section)

---

## Category 9: Audit Logging Service

### T-029: Create Audit Service project scaffold

- **Description**: Create the Audit Service project structure: `services/audit/` with `src/main.py` (FastAPI app), `src/handlers.py`, `src/writer.py`, `Dockerfile`, `requirements.txt`. Include health check endpoints and Dapr app-id annotation. Configure database connection (via Dapr Secrets Store) for writing to activity_log table.
- **Spec refs**: FR-049 (health checks), FR-019–023a (audit logging)
- **Plan refs**: Plan §2.1 (Audit Service), Plan §7.1 (services/audit/ layout)
- **Preconditions**: T-013 (activity_log table exists)
- **Expected output**: Service starts, health endpoints return 200; Docker image builds; can connect to PostgreSQL
- **Files to modify/create**:
  - `services/audit/src/__init__.py` (NEW)
  - `services/audit/src/main.py` (NEW)
  - `services/audit/src/handlers.py` (NEW)
  - `services/audit/src/writer.py` (NEW)
  - `services/audit/Dockerfile` (NEW)
  - `services/audit/requirements.txt` (NEW)

---

### T-030: Implement event-to-audit-log writer

- **Description**: In the Audit Service, implement the `writer.py` module that receives a CloudEvent (task or reminder event) and writes an immutable ActivityLogEntry to PostgreSQL. Extract: user_id, task_id, action_type, actor (user or system), changed_fields (JSONB with old/new values), timestamp.
- **Spec refs**: FR-019 (log every mutation), FR-020 (entry includes timestamp, user_id, action, task_id, changed fields), FR-021 (system actor for auto-generated), FR-023 (durable, survive restarts)
- **Plan refs**: Plan §3.5 (Use Case 3 — writes immutable entry)
- **Preconditions**: T-029 (scaffold), T-014 (ActivityLogEntry model)
- **Expected output**: Each event → one ActivityLogEntry row in PostgreSQL; fields correctly extracted from CloudEvent; idempotent (duplicate event ID doesn't create duplicate entry)
- **Files to modify/create**:
  - `services/audit/src/writer.py` (EXTEND)

---

### T-031: Implement audit event handlers and publish sync events

- **Description**: In the Audit Service, implement handlers for all subscribed topics: `task.*` from `task-events` and `reminder.*` from `reminders`. After writing the log entry, publish `audit.entry-created` event to `task-updates` topic for WebSocket Gateway to broadcast.
- **Spec refs**: FR-019 (log every mutation), FR-034 (real-time notifications from event stream)
- **Plan refs**: Plan §4.2 (Audit subscribes to task-events and reminders), Plan §3.3 (Audit produces to task-updates)
- **Preconditions**: T-030 (writer works)
- **Expected output**: Events from all sources create audit entries; `audit.entry-created` published to `task-updates`; WebSocket Gateway can receive these
- **Files to modify/create**:
  - `services/audit/src/handlers.py` (EXTEND)

---

### T-032: Implement activity log 90-day pruning job

- **Description**: In the Audit Service, register a Dapr cron job (daily at 02:00 UTC) that deletes activity_log entries older than 90 days.
- **Spec refs**: FR-023a (90-day retention, automatic pruning)
- **Plan refs**: Plan §4.5 (Jobs table — Activity pruning cron)
- **Preconditions**: T-030 (entries exist to prune)
- **Expected output**: Entries older than 90 days are deleted daily; entries within 90 days are untouched
- **Files to modify/create**:
  - `services/audit/src/main.py` (EXTEND — register Dapr job handler)

---

### T-033: Create activity log API endpoints

- **Description**: Create `GET /api/v1/activity` and `GET /api/v1/tasks/{task_id}/activity` endpoints in the Chat API. Return paginated activity log entries (20 per page, newest first). Query PostgreSQL activity_log table filtered by user_id (and optionally task_id).
- **Spec refs**: FR-022 (display activity log, paginated, newest-first)
- **Plan refs**: Plan §6.2 (GET /api/v1/activity, GET /api/v1/tasks/{id}/activity)
- **Preconditions**: T-013, T-014 (activity_log table + model)
- **Expected output**: Paginated JSON response with entries, total count, page number; filtered by authenticated user; optionally by task_id
- **Files to modify/create**:
  - `api/src/routes/activity.py` (NEW)
  - `api/src/services/activity_service.py` (NEW)
  - `api/src/routes/__init__.py` (EXTEND — mount activity router)

---

### T-034: Create Audit Service Dockerfile and Helm templates

- **Description**: Create the Dockerfile for the Audit Service and the Helm Deployment + Service templates. Include Dapr annotations (app-id: `audit-service`, app-port, protocol). Configure resource limits (256Mi/250m).
- **Spec refs**: FR-036 (all services in local deployment)
- **Plan refs**: Plan §2.3 (Resource Budgets), Plan §7.1 (infra layout)
- **Preconditions**: T-029 (service scaffold)
- **Expected output**: `docker build` succeeds; Helm template renders valid YAML; pod deploys with Dapr sidecar
- **Files to modify/create**:
  - `infra/docker/audit.Dockerfile` (NEW)
  - `infra/helm/pakaura/templates/audit/deployment.yaml` (NEW)
  - `infra/helm/pakaura/templates/audit/service.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — add audit section)

---

## Category 10: WebSocket Real-Time Sync

### T-035: Create WebSocket Gateway project scaffold

- **Description**: Create the WebSocket Gateway project structure: `services/websocket-gateway/` with `src/main.py` (FastAPI + WebSocket), `src/connections.py`, `src/handlers.py`, `Dockerfile`, `requirements.txt`. Include health check endpoints and Dapr app-id annotation.
- **Spec refs**: FR-049 (health checks), FR-024–026 (real-time sync)
- **Plan refs**: Plan §2.1 (WebSocket Gateway), Plan §7.1 (services/websocket-gateway/ layout)
- **Preconditions**: None
- **Expected output**: Service starts, health endpoints return 200; WebSocket upgrade endpoint accepts connections; Docker image builds
- **Files to modify/create**:
  - `services/websocket-gateway/src/__init__.py` (NEW)
  - `services/websocket-gateway/src/main.py` (NEW)
  - `services/websocket-gateway/src/connections.py` (NEW)
  - `services/websocket-gateway/src/handlers.py` (NEW)
  - `services/websocket-gateway/Dockerfile` (NEW)
  - `services/websocket-gateway/requirements.txt` (NEW)

---

### T-036: Implement per-user WebSocket connection manager

- **Description**: In the WebSocket Gateway, implement the connection manager that tracks active WebSocket connections per user. Use Dapr State Store to map `ws:user:{user_id}` → list of connection IDs. Handle JWT authentication on connection upgrade. Handle disconnect cleanup.
- **Spec refs**: FR-024 (push to all active sessions), FR-026 (handle disconnection gracefully)
- **Plan refs**: Plan §4.3 (State Store — ws:user:{user_id} pattern), Plan §6.3 (WS /ws/{user_id})
- **Preconditions**: T-035 (scaffold), T-007 (Dapr state store)
- **Expected output**: Multiple WS connections for same user tracked; disconnect removes from state; JWT validated on upgrade
- **Files to modify/create**:
  - `services/websocket-gateway/src/connections.py` (EXTEND)
  - `services/websocket-gateway/src/main.py` (EXTEND)

---

### T-037: Implement Dapr event handlers for real-time push

- **Description**: In the WebSocket Gateway, implement handlers for: `sync.task-changed` and `audit.entry-created` from `task-updates` topic, and `reminder.fired` from `reminders` topic. On receiving an event, look up the user's connections and push the event payload to all connected WebSocket sessions.
- **Spec refs**: FR-024 (push within 3 seconds, SC-005), FR-025 (push reminders to all sessions), FR-034 (driven by event stream, not polling)
- **Plan refs**: Plan §4.2 (WS Gateway subscriptions), Plan §3.5 (Use Case 4 — Real-Time Sync)
- **Preconditions**: T-036 (connection manager), T-006 (Dapr pubsub), T-009 (subscriptions)
- **Expected output**: Task change in one browser tab appears in another within 3 seconds; reminder notification pushed to all sessions
- **Files to modify/create**:
  - `services/websocket-gateway/src/handlers.py` (EXTEND)

---

### T-038: Implement WebSocket reconnection and catchup

- **Description**: Implement the client catchup protocol: when a client reconnects, it sends `{ "type": "catchup", "since": "ISO8601" }` via WebSocket. The Gateway queries the activity_log (or a recent events cache) for events since that timestamp and pushes them to the reconnected client.
- **Spec refs**: FR-026 (reconcile missed events on reconnect)
- **Plan refs**: Plan §6.3 (WS reconnect — client sends catchup)
- **Preconditions**: T-036, T-037 (connection manager + event handlers)
- **Expected output**: After disconnect/reconnect, client receives all missed events; state is consistent with server
- **Files to modify/create**:
  - `services/websocket-gateway/src/handlers.py` (EXTEND)
  - `services/websocket-gateway/src/main.py` (EXTEND)

---

### T-039: Create WebSocket Gateway Dockerfile and Helm templates

- **Description**: Create the Dockerfile for the WebSocket Gateway and the Helm Deployment + Service templates. Include Dapr annotations (app-id: `websocket-gateway`, app-port, protocol). Configure resource limits (256Mi/250m).
- **Spec refs**: FR-036 (all services in local deployment)
- **Plan refs**: Plan §2.3 (Resource Budgets), Plan §7.1 (infra layout)
- **Preconditions**: T-035 (service scaffold)
- **Expected output**: `docker build` succeeds; Helm template renders valid YAML; pod deploys with Dapr sidecar
- **Files to modify/create**:
  - `infra/docker/websocket-gateway.Dockerfile` (NEW)
  - `infra/helm/pakaura/templates/websocket-gateway/deployment.yaml` (NEW)
  - `infra/helm/pakaura/templates/websocket-gateway/service.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — add websocket-gateway section)

---

## Category 11: Frontend Enhancements

### T-040: Create WebSocket client hook and library

- **Description**: Create `useWebSocket.ts` hook and `websocket.ts` utility for the frontend. Manages WebSocket connection to `/ws/{user_id}`, handles JWT auth, automatic reconnection with exponential backoff, and catchup protocol on reconnect.
- **Spec refs**: FR-024 (real-time push), FR-026 (reconnection with reconciliation)
- **Plan refs**: Plan §7.1 (frontend hooks + lib)
- **Preconditions**: T-035 (WebSocket Gateway exists to connect to)
- **Expected output**: Hook connects to WS Gateway; auto-reconnects on disconnect; sends catchup request; exposes incoming events to React components
- **Files to modify/create**:
  - `frontend/src/hooks/useWebSocket.ts` (NEW)
  - `frontend/src/lib/websocket.ts` (NEW)

---

### T-041: Create real-time sync hook for task state

- **Description**: Create `useRealTimeSync.ts` hook that listens to WebSocket events (sync.task-changed) and updates the local task list state in real time. Integrates with the existing task list data fetching.
- **Spec refs**: FR-024 (task changes in all sessions within 3 seconds), SC-005
- **Plan refs**: Plan §7.1 (useRealTimeSync.ts)
- **Preconditions**: T-040 (WebSocket hook)
- **Expected output**: Task created/updated/deleted in one tab appears in another tab within 3 seconds without refresh
- **Files to modify/create**:
  - `frontend/src/hooks/useRealTimeSync.ts` (NEW)

---

### T-042: Extend TaskForm with due date, priority, tags, and recurrence

- **Description**: Extend the existing TaskForm component to include: date/time picker for due date, dropdown for reminder lead time (15min/30min/1hr/1day/none), priority selector (none/low/medium/high/urgent), tag input with auto-complete from `GET /api/v1/tags`, recurrence pattern selector (daily/weekly/monthly/custom).
- **Spec refs**: FR-001 (set due date), FR-005 (configure lead time), FR-010 (priority levels), FR-012–014 (tags + auto-complete), FR-007 (recurrence patterns), SC-001 (<10s flow)
- **Plan refs**: Plan §7.1 (TaskForm.tsx EXTEND)
- **Preconditions**: T-015, T-016, T-017 (API endpoints for new fields)
- **Expected output**: Form renders all new fields; submits create/update with all fields; auto-complete works for tags
- **Files to modify/create**:
  - `frontend/src/components/tasks/TaskForm.tsx` (EXTEND)
  - `frontend/src/lib/api.ts` (EXTEND — new params on create/update)
  - `frontend/src/types/task.ts` (EXTEND — new fields)

---

### T-043: Extend TaskItem with due date display, priority badge, tags, and overdue indicator

- **Description**: Extend the existing TaskItem component to display: due date with relative time, priority badge with color coding (urgent=red, high=orange, medium=yellow, low=blue, none=gray), tag chips, and overdue visual indicator (red highlight for past due + incomplete).
- **Spec refs**: FR-003 (overdue visual indicator), FR-010 (priority visual), US-1 scenario 4, US-3 scenario 1
- **Plan refs**: Plan §7.1 (TaskItem.tsx EXTEND)
- **Preconditions**: T-042 (tasks have new fields to display)
- **Expected output**: Task items show all new visual elements; overdue tasks highlighted; priority badges color-coded
- **Files to modify/create**:
  - `frontend/src/components/tasks/TaskItem.tsx` (EXTEND)

---

### T-044: Create TaskFilters component (search, filter, sort)

- **Description**: Create a new TaskFilters component with: search input (keyword), filter dropdowns (status, priority, tag, due date range, overdue), sort selector (due_date/priority/created_at/title + asc/desc). Sends query parameters to `GET /api/v1/tasks`.
- **Spec refs**: FR-015–018 (search, filter, sort, combined AND)
- **Plan refs**: Plan §7.1 (TaskFilters.tsx NEW)
- **Preconditions**: T-018 (API supports filter/sort params)
- **Expected output**: Filters apply correctly; results update on filter change; search + filters combine with AND logic
- **Files to modify/create**:
  - `frontend/src/components/tasks/TaskFilters.tsx` (NEW)
  - `frontend/src/components/tasks/TaskList.tsx` (EXTEND — integrate filters)

---

### T-045: Create ActivityLog page and component

- **Description**: Create the activity log page at `/activity` and the `ActivityLog.tsx` component. Displays paginated entries (20/page, newest first) from `GET /api/v1/activity`. Shows action type, task title, timestamp, actor, changed fields with old/new values.
- **Spec refs**: FR-022 (paginated activity log, 20/page, newest-first), US-6 scenarios
- **Plan refs**: Plan §7.1 (activity/page.tsx NEW, ActivityLog.tsx NEW)
- **Preconditions**: T-033 (activity API endpoint)
- **Expected output**: Page renders activity entries; pagination works; shows field-level change detail
- **Files to modify/create**:
  - `frontend/src/app/(protected)/activity/page.tsx` (NEW)
  - `frontend/src/components/activity/ActivityLog.tsx` (NEW)
  - `frontend/src/types/activity.ts` (NEW)
  - `frontend/src/lib/api.ts` (EXTEND — activity endpoint)

---

### T-046: Create ReminderToast notification component

- **Description**: Create the `ReminderToast.tsx` component that displays an in-app notification when a `reminder.fired` event is received via WebSocket. Shows task title, due date, and a dismiss button. Supports multiple simultaneous notifications.
- **Spec refs**: FR-004 (in-app reminder notification), FR-025 (push to all sessions), US-1 scenario 2
- **Plan refs**: Plan §7.1 (ReminderToast.tsx NEW)
- **Preconditions**: T-040 (WebSocket hook receives reminder events)
- **Expected output**: Toast appears when reminder fires; shows relevant task info; dismissible; multiple toasts stack
- **Files to modify/create**:
  - `frontend/src/components/notifications/ReminderToast.tsx` (NEW)

---

## Category 12: Helm Chart Extensions

### T-047: Update Chart.yaml version and add Dapr annotations to API deployment

- **Description**: Bump Helm chart version to 5.0.0 in Chart.yaml. Add Dapr sidecar injection annotations to the API deployment template: `dapr.io/enabled: "true"`, `dapr.io/app-id: "api"`, `dapr.io/app-port`. Add new environment variables for Dapr configuration.
- **Spec refs**: FR-036 (abstraction layer sidecars), Infrastructure Abstraction Requirements
- **Plan refs**: Plan §8.3 (Helm Chart Reuse — api extended with Dapr)
- **Preconditions**: T-004 (Dapr installed on cluster)
- **Expected output**: API pod has Dapr sidecar container injected; `kubectl get pods -n pakaura` shows 2/2 containers for api pod
- **Files to modify/create**:
  - `infra/helm/pakaura/Chart.yaml` (UPDATE — version 5.0.0)
  - `infra/helm/pakaura/templates/api/deployment.yaml` (EXTEND — Dapr annotations)

---

### T-048: Extend values.yaml with all new service configurations

- **Description**: Add configuration sections for all new services (notification, recurring, audit, websocket-gateway), Kafka, Dapr components, and monitoring to the main `values.yaml`. Include image repos, resource limits, replica counts, and service ports.
- **Spec refs**: FR-036 (all services), FR-035 (Helm charts evolved from Phase IV)
- **Plan refs**: Plan §2.3 (Resource Budgets), Plan §8.3 (values.yaml shared defaults)
- **Preconditions**: T-001 (Kafka section), T-006–T-009 (Dapr sections)
- **Expected output**: `helm template` renders all services without errors; all resource limits match plan budgets
- **Files to modify/create**:
  - `infra/helm/pakaura/values.yaml` (EXTEND)

---

### T-049: Extend values-local.yaml with local development overrides

- **Description**: Extend `values-local.yaml` with local-specific overrides for all new services: `imagePullPolicy: Never`, single Kafka broker, in-memory Dapr state store, 1 replica each, local secret values.
- **Spec refs**: FR-037 (reproducible from single Helm install), FR-038 (values-local.yaml convention)
- **Plan refs**: Plan §8.1 (Local-specific configuration table), Plan §8.3 (values layering)
- **Preconditions**: T-048 (base values exist)
- **Expected output**: `helm install -f values-local.yaml` renders all services with local overrides applied
- **Files to modify/create**:
  - `infra/helm/pakaura/values-local.yaml` (EXTEND)

---

### T-050: Create values-production.yaml with OKE configuration

- **Description**: Create `values-production.yaml` with Oracle OKE production configuration: OCIR image registry, `imagePullPolicy: Always`, managed Kafka broker endpoint, Redis state store, TLS/Ingress config, multi-replica settings (2 for API, Frontend, WS Gateway).
- **Spec refs**: FR-039–043 (production deployment requirements)
- **Plan refs**: Plan §8.2 (Production-specific configuration table), Plan §8.3 (values layering)
- **Preconditions**: T-048 (base values exist), T-003 (Kafka prod config)
- **Expected output**: `values-production.yaml` exists; `helm template -f values-production.yaml` renders valid manifests with production settings
- **Files to modify/create**:
  - `infra/helm/pakaura/values-production.yaml` (NEW or EXTEND from T-003)

---

### T-051: Extend _helpers.tpl with new service label helpers

- **Description**: Add Helm template helper functions for the new services (notification, recurring, audit, websocket-gateway) that generate consistent labels and selector labels.
- **Spec refs**: FR-035 (Helm charts evolved from Phase IV)
- **Plan refs**: Plan §7.1 (templates/_helpers.tpl EXTEND)
- **Preconditions**: Existing _helpers.tpl from Phase IV
- **Expected output**: All new service templates can use `include "pakaura.labels"` consistently
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/_helpers.tpl` (EXTEND)

---

### T-052: Extend configmap and secrets templates for new services

- **Description**: Extend the Helm configmap template with new environment variables needed by Phase V services (AI model config, event topics, Dapr config). Extend secrets template with KAFKA_SASL_PASSWORD (production).
- **Spec refs**: FR-042 (K8s secrets for sensitive config)
- **Plan refs**: Plan §8.3 (templates/configmap and secrets extended)
- **Preconditions**: Existing configmap.yaml and secrets.yaml from Phase IV
- **Expected output**: ConfigMap contains all new env vars; Secret contains all new sensitive values
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/configmap.yaml` (EXTEND)
  - `infra/helm/pakaura/templates/secrets.yaml` (EXTEND)

---

## Category 13: Minikube Deployment

### T-053: Create build-all-images script/Makefile

- **Description**: Create a Makefile or shell script that builds all 6 Docker images (api, frontend, notification, recurring, audit, websocket-gateway) and loads them into Minikube. Single command entry point for local builds.
- **Spec refs**: FR-037 (reproducible from single command plus image builds)
- **Plan refs**: Plan §8.1 (Reproducibility)
- **Preconditions**: All Dockerfiles exist (T-024, T-028, T-034, T-039 + existing)
- **Expected output**: `make build-all` (or equivalent) builds and loads all 6 images; `minikube image ls` shows all images
- **Files to modify/create**:
  - `Makefile` (NEW or EXTEND)

---

### T-054: Validate full Minikube deployment end-to-end

- **Description**: Deploy the complete Phase V system to Minikube using `helm install pakaura ... -f values-local.yaml`. Verify all pods reach Running state, all Dapr sidecars inject, Kafka topics exist, health endpoints respond, and port-forward provides access to frontend and API.
- **Spec refs**: FR-035 (deploy to Minikube), FR-036 (all services running), FR-037 (single Helm install), SC-013 (pods running within 5 minutes)
- **Plan refs**: Plan §8.1 (full Minikube steps)
- **Preconditions**: All previous tasks (services built, Helm charts complete, Dapr configured)
- **Expected output**: `kubectl get pods -n pakaura` shows all pods Running/Ready; port-forward works; create task → event flows through pipeline → appears in activity log → syncs across sessions
- **Files to modify/create**:
  - None (validation task)

---

## Category 14: Cloud Deployment (Oracle OKE)

### T-055: Provision Oracle OKE cluster

- **Description**: Provision an Oracle Container Engine for Kubernetes (OKE) cluster via Oracle Cloud Console or Terraform. Configure node pool with sufficient resources for all services. Set up kubeconfig for kubectl access.
- **Spec refs**: FR-039 (deploy to OKE)
- **Plan refs**: Plan §8.2 step 1 (OKE cluster provisioned)
- **Preconditions**: Oracle Cloud account
- **Expected output**: `kubectl get nodes` (pointing to OKE) shows healthy nodes; cluster accessible from local machine
- **Files to modify/create**:
  - None (cloud console operation)

---

### T-056: Configure OCIR container registry and push images

- **Description**: Configure Oracle Container Image Registry (OCIR). Tag all 6 Docker images for OCIR and push them. Verify images are accessible from the OKE cluster.
- **Spec refs**: FR-039 (deploy to OKE), FR-045 (push images to container registry)
- **Plan refs**: Plan §8.2 steps 4–5 (push to OCIR)
- **Preconditions**: T-055 (OKE cluster), all Docker images built
- **Expected output**: All 6 images visible in OCIR; OKE can pull images
- **Files to modify/create**:
  - None (registry operations)

---

### T-057: Deploy Phase V to OKE with production values

- **Description**: Install Dapr on OKE cluster. Deploy the full system using `helm install -f values-production.yaml`. Configure managed Kafka/PostgreSQL endpoints. Verify all pods Running with Dapr sidecars.
- **Spec refs**: FR-039 (deploy to OKE), FR-040 (managed services), FR-043 (survive pod restarts)
- **Plan refs**: Plan §8.2 (full OKE steps 1–5)
- **Preconditions**: T-055, T-056, T-050 (cluster + images + prod values)
- **Expected output**: `kubectl get pods -n pakaura` on OKE shows all pods Running; all services accessible within cluster
- **Files to modify/create**:
  - None (deployment operation)

---

### T-058: Configure Ingress with TLS for production HTTPS

- **Description**: Deploy an Ingress controller (nginx or Oracle native) on OKE. Create Ingress resource routing to frontend and API services. Configure TLS certificate (Let's Encrypt or Oracle-managed) for HTTPS access.
- **Spec refs**: FR-041 (HTTPS endpoint with valid domain or IP)
- **Plan refs**: Plan §8.2 step 6 (Ingress + TLS)
- **Preconditions**: T-057 (services deployed on OKE)
- **Expected output**: `https://<domain>` loads the frontend; API accessible at `https://<domain>/api/v1/`; valid TLS certificate
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/ingress.yaml` (NEW)
  - `infra/helm/pakaura/values-production.yaml` (EXTEND — ingress config)

---

### T-059: Validate production deployment end-to-end

- **Description**: Access the production URL and verify: user registration/login, task CRUD with all Phase V features, event pipeline (recurring, reminders, audit log), real-time sync across two browser tabs, AI chatbot with new commands, monitoring dashboard.
- **Spec refs**: SC-010 (production accessible, all features work), SC-012 (no regression)
- **Plan refs**: Plan §8.2, spec Demo Flow
- **Preconditions**: T-057, T-058 (production deployed with HTTPS)
- **Expected output**: All demo flow steps pass on production; no feature regression from Phase II/III/IV
- **Files to modify/create**:
  - None (validation task)

---

## Category 15: CI/CD Pipeline

### T-060: Create GitHub Actions test stage

- **Description**: Create `.github/workflows/deploy.yml` with Stage 1 (TEST): run `pytest` for api/ and all 4 services, run `npm test` for frontend. Triggered on push to `main` and all branches. Stage must fail and block if any test fails.
- **Spec refs**: FR-044 (GitHub Actions), FR-046 (fail on test failure)
- **Plan refs**: Plan §9.1 (Stage 1: TEST), Plan §9.4 (feature branch behavior)
- **Preconditions**: Tests exist for all services
- **Expected output**: Push triggers test stage; all tests run; failure blocks subsequent stages
- **Files to modify/create**:
  - `.github/workflows/deploy.yml` (NEW)

---

### T-061: Create GitHub Actions build stage

- **Description**: Add Stage 2 (BUILD) to the pipeline: build all 6 Docker images, tag with git SHA + "latest", push to OCIR. Runs after Stage 1 passes. Triggered on both main and feature branches.
- **Spec refs**: FR-045 (build Docker images, push to registry)
- **Plan refs**: Plan §9.1 (Stage 2: BUILD), Plan §9.2 (Pipeline Secrets)
- **Preconditions**: T-060 (test stage), T-056 (OCIR configured)
- **Expected output**: Docker images built and pushed to OCIR with git SHA tags; visible in registry
- **Files to modify/create**:
  - `.github/workflows/deploy.yml` (EXTEND)

---

### T-062: Create GitHub Actions deploy stage

- **Description**: Add Stage 3 (DEPLOY) to the pipeline: configure kubectl for OKE, run `helm upgrade --install -f values-production.yaml`, wait for rollout status. Only runs on `main` branch pushes.
- **Spec refs**: FR-045 (deploy to production cluster on main push)
- **Plan refs**: Plan §9.1 (Stage 3: DEPLOY — main branch only), Plan §9.2 (OKE_KUBECONFIG secret)
- **Preconditions**: T-061 (build stage), T-057 (OKE cluster working)
- **Expected output**: Merge to main → automatic deployment to OKE; all deployments roll out successfully
- **Files to modify/create**:
  - `.github/workflows/deploy.yml` (EXTEND)

---

### T-063: Create GitHub Actions verify stage

- **Description**: Add Stage 4 (VERIFY) to the pipeline: health check curl to production URL, smoke test (register + create task + verify API response). Only runs after deploy stage on main branch.
- **Spec refs**: FR-045 (deploy and verify), SC-009 (<15 min total)
- **Plan refs**: Plan §9.1 (Stage 4: VERIFY)
- **Preconditions**: T-062 (deploy stage)
- **Expected output**: Post-deploy verification passes; health endpoints return 200; smoke test creates a task successfully
- **Files to modify/create**:
  - `.github/workflows/deploy.yml` (EXTEND)

---

### T-064: Create manual rollback workflow

- **Description**: Create a GitHub Actions `workflow_dispatch` workflow that accepts a Helm revision number as input and runs `helm rollback pakaura <revision> -n pakaura` on the OKE cluster.
- **Spec refs**: FR-047 (manual rollback support)
- **Plan refs**: Plan §9.3 (Rollback Strategy)
- **Preconditions**: T-062 (deploy stage creates revisions)
- **Expected output**: Manual trigger with revision number → rollback executed; `helm history` shows rollback
- **Files to modify/create**:
  - `.github/workflows/deploy.yml` (EXTEND — add workflow_dispatch)

---

## Category 16: Monitoring & Logging

### T-065: Add structured JSON logging to all services

- **Description**: Configure all Python services (API, notification, recurring, audit, websocket-gateway) to emit structured JSON logs with fields: timestamp, level, service, message, and optional task_id/user_id/correlation_id.
- **Spec refs**: FR-048 (structured JSON logs)
- **Plan refs**: Plan §10.2 (Structured Logging)
- **Preconditions**: All service scaffolds exist
- **Expected output**: `kubectl logs <pod>` shows JSON-formatted log lines; parseable by Loki/Promtail
- **Files to modify/create**:
  - `api/src/main.py` (EXTEND — logging config)
  - `services/notification/src/main.py` (EXTEND)
  - `services/recurring/src/main.py` (EXTEND)
  - `services/audit/src/main.py` (EXTEND)
  - `services/websocket-gateway/src/main.py` (EXTEND)

---

### T-066: Add health check endpoints to all services

- **Description**: Add `/health/ready` (readiness) and `/health/live` (liveness) endpoints to all Python services. Readiness checks dependencies (DB connection, Dapr sidecar, Kafka connectivity). Liveness checks process is running.
- **Spec refs**: FR-049 (readiness and liveness probes)
- **Plan refs**: Plan §10.4 (Health Checks)
- **Preconditions**: All service scaffolds exist
- **Expected output**: All `/health/ready` return 200 when dependencies are up (503 otherwise); `/health/live` always returns 200 if process is running
- **Files to modify/create**:
  - `api/src/routes/health.py` (NEW or EXTEND existing /api/v1/health)
  - `services/notification/src/main.py` (EXTEND)
  - `services/recurring/src/main.py` (EXTEND)
  - `services/audit/src/main.py` (EXTEND)
  - `services/websocket-gateway/src/main.py` (EXTEND)

---

### T-067: Add Prometheus metrics to all services

- **Description**: Add Prometheus metrics instrumentation to all services using `prometheus-fastapi-instrumentator` or similar. Expose: http_requests_total, http_request_duration_seconds (histogram), http_responses_by_status. Add custom metrics: events_published_total, events_processed_total, websocket_active_connections, reminder_delivery_latency_seconds.
- **Spec refs**: FR-050 (request rate, error rate, response latency, event lag, WS connections)
- **Plan refs**: Plan §10.3 (Metrics table)
- **Preconditions**: All service scaffolds exist
- **Expected output**: `/metrics` endpoint on each service returns Prometheus-formatted metrics; all 8 metric types present
- **Files to modify/create**:
  - `api/src/main.py` (EXTEND)
  - `services/notification/src/main.py` (EXTEND)
  - `services/recurring/src/main.py` (EXTEND)
  - `services/audit/src/main.py` (EXTEND)
  - `services/websocket-gateway/src/main.py` (EXTEND)

---

### T-068: Create Prometheus + Grafana Helm templates

- **Description**: Create Helm templates for the monitoring stack: Prometheus (scrape config targeting all services + Kafka exporter), Grafana (with Prometheus and Loki as datasources). Include Promtail DaemonSet for log shipping to Loki.
- **Spec refs**: FR-048 (centralized log aggregator), FR-051 (dashboard accessible to operators), SC-011 (monitoring dashboard)
- **Plan refs**: Plan §10.1 (Stack table), Plan §7.1 (templates/monitoring/)
- **Preconditions**: T-067 (services expose metrics)
- **Expected output**: Prometheus scrapes all services; Grafana accessible; Loki receives logs from all pods
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/monitoring/prometheus.yaml` (NEW)
  - `infra/helm/pakaura/templates/monitoring/grafana.yaml` (NEW)
  - `infra/helm/pakaura/templates/monitoring/loki.yaml` (NEW)
  - `infra/helm/pakaura/templates/monitoring/promtail.yaml` (NEW)
  - `infra/helm/pakaura/values.yaml` (EXTEND — monitoring section)

---

### T-069: Create pre-configured Grafana dashboards

- **Description**: Create Grafana dashboard JSON files for the 4 dashboards: System Overview, Kafka Events, WebSocket, Reminders. Load via ConfigMap or Grafana provisioning.
- **Spec refs**: FR-051 (dashboard accessible), SC-011 (consumer lag visible)
- **Plan refs**: Plan §10.5 (Grafana Dashboards — 4 dashboards)
- **Preconditions**: T-068 (Grafana deployed)
- **Expected output**: Grafana shows 4 pre-loaded dashboards; panels show live data; Kafka consumer lag visible
- **Files to modify/create**:
  - `infra/helm/pakaura/templates/monitoring/grafana-dashboards-configmap.yaml` (NEW)

---

## Category 17: AI Chatbot Extension

### T-070: Extend AI chatbot intent detection for Phase V commands

- **Description**: Extend the AI chatbot's intent router to recognize new intents: set_due_date, set_priority, add_tag, remove_tag, create_recurring_task, show_overdue, query_activity_log. Map natural language patterns to these intents.
- **Spec refs**: FR-027 (natural language for due dates, priorities, tags, recurring, overdue, activity log)
- **Plan refs**: Plan §2.1 (Chat API extended), Plan §7.1 (ai.py EXTEND)
- **Preconditions**: T-015–T-019 (API endpoints for new features)
- **Expected output**: AI correctly identifies intent for each new command type with ≥90% accuracy (SC-014)
- **Files to modify/create**:
  - `api/src/routes/ai.py` (EXTEND)
  - `api/src/ai/agent.py` (EXTEND — if exists)

---

### T-071: Implement AI chatbot handlers for Phase V actions

- **Description**: Implement the action handlers that execute each new intent: call the appropriate API endpoints to set due dates, change priorities, add/remove tags, create recurring tasks, filter overdue tasks, and query the activity log. Return natural language responses.
- **Spec refs**: FR-027 (execute new commands), FR-028 (maintain existing Phase III commands), US-8 scenarios
- **Plan refs**: Plan §2.1 (Chat API — AI chatbot), Plan §6.1–6.2 (API endpoints to call)
- **Preconditions**: T-070 (intents detected), T-015–T-019, T-033 (API endpoints working)
- **Expected output**: "Set due date for my report to Friday" → task updated with due date; "Show overdue tasks" → filtered list returned; all existing commands still work
- **Files to modify/create**:
  - `api/src/routes/ai.py` (EXTEND)
  - `api/src/ai/agent.py` (EXTEND — if exists)
  - `api/src/mcp_server/task_operations.py` (EXTEND — if exists)

---

## Category 18: Documentation & Demo

### T-072: Update README with Phase V deployment instructions

- **Description**: Update the project README with Phase V deployment instructions for both local (Minikube) and production (OKE). Include prerequisites (Dapr CLI, Minikube, kubectl), build commands, deploy commands, port-forward instructions, and verification steps.
- **Spec refs**: Submission Requirements (README updated with Phase V deployment instructions)
- **Plan refs**: Plan §8.1 (Minikube steps), Plan §8.2 (OKE steps)
- **Preconditions**: T-054 (Minikube validated), T-059 (production validated)
- **Expected output**: New developer can follow README to deploy Phase V locally from scratch
- **Files to modify/create**:
  - `README.md` (EXTEND)

---

### T-073: Create demo video script and recording

- **Description**: Record a screen capture demo video following the spec's Demo Flow order (12 steps): show K8s cluster, event infrastructure, register/login, create task with advanced features, recurring task, search/filter, real-time sync, reminder, activity log, AI chatbot, CI/CD pipeline, monitoring dashboard.
- **Spec refs**: Demo & Submission Requirements (demo video showing complete flow)
- **Plan refs**: Spec Demo Flow (12 steps)
- **Preconditions**: T-059 (production working), all features implemented
- **Expected output**: Demo video file covering all 12 demo steps; clear audio/captions explaining each step
- **Files to modify/create**:
  - None (video file)

---

### T-074: Create Phase V documentation package

- **Description**: Compile Phase V submission package: spec.md, plan.md, tasks.md, updated README, Helm charts, CI/CD config, architecture diagrams, demo video link. Tag the repository with Phase V release.
- **Spec refs**: Submission Requirements (single repo, branch/tag identified, README, demo video, Helm charts, CI/CD)
- **Plan refs**: All plan sections
- **Preconditions**: All tasks complete
- **Expected output**: Tagged release; all submission artifacts present; evaluator can deploy and verify
- **Files to modify/create**:
  - None (compilation and tagging)

---

## Dependency Graph (Critical Path)

```
Infrastructure Foundation:
  T-001 → T-002 → T-006 → T-009
  T-004 → T-006, T-007, T-008
  T-013 → T-014

Backend Core (parallel after foundation):
  T-014 → T-015 → T-016, T-017, T-018, T-019
  T-010 → T-011 → T-012

Services (parallel, after T-006 + T-009):
  T-020 → T-021 → T-022 → T-023 → T-024
  T-025 → T-026 → T-027 → T-028
  T-029 → T-030 → T-031 → T-032 → T-034
  T-035 → T-036 → T-037 → T-038 → T-039

Frontend (parallel, after backend APIs):
  T-040 → T-041
  T-042 → T-043 → T-044
  T-045, T-046

Helm & Deploy (after services + charts):
  T-047–T-052 → T-053 → T-054
  T-055 → T-056 → T-057 → T-058 → T-059

CI/CD (after OKE):
  T-060 → T-061 → T-062 → T-063
  T-064

Monitoring (parallel with deploy):
  T-065, T-066, T-067 → T-068 → T-069

AI + Docs (final):
  T-070 → T-071
  T-072 → T-073 → T-074
```

---

## Summary

| Category | Tasks | Range |
|----------|-------|-------|
| 1. Kafka Setup | 3 | T-001 – T-003 |
| 2. Dapr Installation | 2 | T-004 – T-005 |
| 3. Dapr Components | 4 | T-006 – T-009 |
| 4. Backend Event Publishing | 3 | T-010 – T-012 |
| 5. Database Schema | 2 | T-013 – T-014 |
| 6. Advanced Task API | 5 | T-015 – T-019 |
| 7. Reminder Service | 5 | T-020 – T-024 |
| 8. Recurring Task Engine | 4 | T-025 – T-028 |
| 9. Audit Logging Service | 6 | T-029 – T-034 |
| 10. WebSocket Real-Time Sync | 5 | T-035 – T-039 |
| 11. Frontend Enhancements | 7 | T-040 – T-046 |
| 12. Helm Chart Extensions | 6 | T-047 – T-052 |
| 13. Minikube Deployment | 2 | T-053 – T-054 |
| 14. Cloud Deployment (OKE) | 5 | T-055 – T-059 |
| 15. CI/CD Pipeline | 5 | T-060 – T-064 |
| 16. Monitoring & Logging | 5 | T-065 – T-069 |
| 17. AI Chatbot Extension | 2 | T-070 – T-071 |
| 18. Documentation & Demo | 3 | T-072 – T-074 |
| **Total** | **74** | **T-001 – T-074** |
