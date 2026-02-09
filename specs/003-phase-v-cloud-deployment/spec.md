# Feature Specification: Phase V – Advanced Cloud Deployment

**Feature Branch**: `003-phase-v-cloud-deployment`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase V Advanced Cloud Deployment with event-driven architecture, Kafka, Dapr, advanced task features (recurring, due dates, priorities, tags, search, activity log, real-time sync), local Minikube and production cloud Kubernetes deployment, CI/CD, monitoring."

**Constitution Reference**: Phase V – Advanced Cloud Deployment. Kafka MUST be used for task reminders, recurring tasks, activity/audit logs, and real-time synchronization. System MUST tolerate restarts. Events MUST be durable and replayable.

---

## Goals

1. Extend the Phase IV task management system with advanced task features: recurring tasks, due dates with reminders, priorities, tags, search/filter/sort, and activity logging.
2. Introduce event-driven architecture using Kafka as the event backbone and Dapr as the infrastructure abstraction layer.
3. Enable real-time task synchronization across multiple browser sessions for the same user.
4. Deploy to a production cloud Kubernetes cluster (Oracle OKE) alongside the existing local Minikube deployment.
5. Automate build, test, and deployment with CI/CD pipelines.
6. Provide observability through centralized logging, metrics, and health monitoring.

## Non-Goals

- Mobile native applications (iOS/Android).
- Multi-user collaboration or shared task lists.
- Email, SMS, or push notification delivery for reminders (in-app only for Phase V).
- Task file attachments or rich media.
- Voice input/output for the AI chatbot.
- Multi-region or geo-distributed deployment.
- Custom user-defined automation rules or workflows.
- Migration away from PostgreSQL to a different primary database.
- Replacing the existing REST API; all new features extend the existing `/api/v1/` surface.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Set Due Date and Receive Reminder (Priority: P1)

An authenticated user sets a due date on a task and receives an in-app reminder before the deadline. The reminder appears in the user interface regardless of which browser tab or session the user is currently using.

**Why this priority**: Due dates and reminders are the highest-value advanced feature. They transform a simple checklist into a time-aware task manager and drive the core event-driven architecture requirement (Kafka events, scheduled jobs).

**Independent Test**: Can be tested by creating a task, setting a due date in the near future, waiting for the reminder window, and verifying the notification appears in-app. Delivers time-aware task management.

**Acceptance Scenarios**:

1. **Given** an authenticated user with an existing task, **When** they set a due date to tomorrow at 9:00 AM, **Then** the due date is saved and displayed on the task.
2. **Given** a task with a due date set, **When** the reminder time arrives (default: 30 minutes before due), **Then** the user sees an in-app notification in all active sessions.
3. **Given** a task with a due date, **When** the user marks the task complete before the due date, **Then** no reminder is sent.
4. **Given** a task whose due date has passed without completion, **When** the user views their task list, **Then** the task is visually marked as overdue.
5. **Given** a user with multiple active browser sessions, **When** a reminder fires, **Then** the notification appears in all sessions simultaneously.

---

### User Story 2 – Create and Manage Recurring Tasks (Priority: P1)

An authenticated user creates a task that automatically recurs on a defined schedule. When the user completes a recurring task instance, the next occurrence is generated automatically.

**Why this priority**: Recurring tasks are a constitution-mandated Kafka use case and represent the most complex event-driven workflow. They validate the event backbone architecture.

**Independent Test**: Can be tested by creating a daily recurring task, completing today's instance, and verifying a new instance is generated for the next day. Delivers automated task scheduling.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they create a task with recurrence set to "daily", **Then** the task is created with a recurrence indicator and the next due date is set to tomorrow.
2. **Given** a recurring task, **When** the user completes the current instance, **Then** a new task instance is automatically created with the next scheduled due date.
3. **Given** a recurring task set to "weekly on Monday", **When** the current Monday instance is completed, **Then** the next instance is created for the following Monday.
4. **Given** a recurring task, **When** the user deletes the recurrence (not just the instance), **Then** no further instances are generated.
5. **Given** a recurring task that the user has not completed by its due date, **When** the next occurrence date arrives, **Then** the overdue instance remains and the new instance is also created.

**Supported Recurrence Patterns**:
- Daily
- Weekly (specific day of week)
- Monthly (specific day of month)
- Custom interval (every N days)

---

### User Story 3 – Assign Priorities to Tasks (Priority: P2)

An authenticated user assigns a priority level to each task. Tasks can be sorted and filtered by priority, and high-priority tasks are visually prominent.

**Why this priority**: Priority management is a fundamental task organization feature that enhances the user's ability to focus on what matters. It is simpler than recurring tasks and can be delivered independently.

**Independent Test**: Can be tested by creating tasks with different priorities and verifying they sort correctly and display appropriate visual indicators. Delivers task prioritization.

**Acceptance Scenarios**:

1. **Given** an authenticated user creating a task, **When** they assign a priority of "high", **Then** the task is saved with that priority and displays a visual indicator (color or icon).
2. **Given** a user viewing their task list, **When** they sort by priority, **Then** tasks are ordered: urgent, high, medium, low, none.
3. **Given** an existing task with no priority, **When** the user updates it to "urgent", **Then** the priority change is saved and reflected immediately.
4. **Given** a user with tasks of mixed priorities, **When** they filter by "high" priority, **Then** only high-priority tasks are displayed.

**Priority Levels**: None (default), Low, Medium, High, Urgent.

---

### User Story 4 – Tag Tasks for Organization (Priority: P2)

An authenticated user applies one or more tags to tasks for flexible categorization. Tasks can be filtered by tag.

**Why this priority**: Tags provide user-defined organization without imposing rigid categories. They complement priorities and support the search/filter feature set.

**Independent Test**: Can be tested by creating tasks with tags and filtering by tag name. Delivers flexible task categorization.

**Acceptance Scenarios**:

1. **Given** an authenticated user creating or editing a task, **When** they add tags "work" and "urgent-review", **Then** the tags are saved and displayed on the task.
2. **Given** a user viewing their task list, **When** they filter by tag "work", **Then** only tasks tagged "work" are shown.
3. **Given** a user, **When** they remove a tag from a task, **Then** the tag is disassociated from that task (but the tag remains available for other tasks).
4. **Given** a user, **When** they type a tag name, **Then** existing tags are suggested for auto-completion.
5. **Given** a user, **When** they apply multiple tag filters, **Then** tasks matching ANY of the selected tags are displayed.

**Tag Rules**:
- Tags are user-scoped (each user has their own tag namespace).
- Tag names: 1–30 characters, alphanumeric plus hyphens, case-insensitive.
- Maximum 10 tags per task.

---

### User Story 5 – Search, Filter, and Sort Tasks (Priority: P2)

An authenticated user can search their tasks by keyword, filter by multiple criteria (status, priority, tag, due date range, overdue), and sort by different fields.

**Why this priority**: Search and filter are essential for users with many tasks. Without them, task lists become unmanageable as they grow.

**Independent Test**: Can be tested by creating a set of diverse tasks and verifying search, filter, and sort produce correct results. Delivers task discoverability.

**Acceptance Scenarios**:

1. **Given** a user with 20+ tasks, **When** they search for "groceries", **Then** all tasks whose title contains "groceries" are displayed.
2. **Given** a user, **When** they filter by status "incomplete" and priority "high", **Then** only incomplete, high-priority tasks are shown.
3. **Given** a user, **When** they sort by due date ascending, **Then** tasks with the nearest due date appear first (tasks without due dates appear at the end).
4. **Given** a user, **When** they filter by "overdue", **Then** only tasks with past due dates that are not completed are shown.
5. **Given** a user, **When** they combine search with filters, **Then** both criteria are applied (AND logic between search and filters).

**Sort Options**: Due date (asc/desc), Priority (high-first/low-first), Created date (newest/oldest), Title (A-Z/Z-A).

**Filter Options**: Status (all/complete/incomplete), Priority level, Tag, Due date range, Overdue flag.

---

### User Story 6 – View Activity / Audit Log (Priority: P3)

An authenticated user can view a chronological log of all actions performed on their tasks. The log captures who did what and when.

**Why this priority**: Activity logging is a constitution-mandated Kafka use case. It provides accountability and helps users understand task history, but is less critical than core task features.

**Independent Test**: Can be tested by performing task actions and verifying each action appears in the activity log with correct details. Delivers task history and accountability.

**Acceptance Scenarios**:

1. **Given** a user who creates a task, **When** they view the activity log, **Then** they see an entry "Task created: [title]" with timestamp.
2. **Given** a user who completes a task, **When** they view the activity log, **Then** they see an entry "Task completed: [title]" with timestamp.
3. **Given** a user who updates a task's priority from "low" to "high", **When** they view the activity log, **Then** they see an entry showing the field changed, old value, and new value.
4. **Given** a user viewing the activity log, **When** they have 100+ entries, **Then** the log is paginated (20 entries per page) and sorted newest-first.
5. **Given** a recurring task that auto-generates a new instance, **When** the user views the log, **Then** they see an entry "Recurring task generated: [title]" attributed to the system.

**Logged Actions**: Task created, updated (with field-level changes), completed, uncompleted, deleted, priority changed, tag added/removed, due date set/changed, recurrence set/changed, reminder sent.

---

### User Story 7 – Real-Time Task Sync Across Sessions (Priority: P3)

When a user has the application open in multiple browser tabs or devices, changes made in one session are reflected in all other sessions in real time without requiring a page refresh.

**Why this priority**: Real-time sync is a constitution-mandated Kafka use case. It provides a modern UX but is not required for core task management functionality.

**Independent Test**: Can be tested by opening two browser tabs, making a change in one, and verifying the change appears in the other within seconds. Delivers multi-session consistency.

**Acceptance Scenarios**:

1. **Given** a user with the app open in two browser tabs, **When** they create a task in tab A, **Then** the task appears in tab B within 3 seconds without refresh.
2. **Given** a user with two sessions, **When** they complete a task in one session, **Then** the task status updates in the other session in real time.
3. **Given** a user whose connection is temporarily lost, **When** the connection is restored, **Then** the session catches up with any missed changes.
4. **Given** a user who closes and reopens a tab, **When** the new tab loads, **Then** it shows the current state of all tasks (not stale data).

---

### User Story 8 – AI Chatbot Manages Advanced Features (Priority: P3)

The existing AI chatbot (Phase III) is extended to support the new task features via natural language. Users can set due dates, priorities, tags, and create recurring tasks through conversation.

**Why this priority**: Extends the existing chatbot to cover new features. Depends on all advanced features being implemented first.

**Independent Test**: Can be tested by issuing natural language commands for each new feature and verifying correct execution. Delivers conversational access to all Phase V features.

**Acceptance Scenarios**:

1. **Given** a user chatting with the AI, **When** they say "Add a task to submit the report by Friday with high priority", **Then** the task is created with the due date set to the coming Friday and priority set to high.
2. **Given** a user, **When** they say "Create a daily recurring task to check emails", **Then** a recurring daily task is created.
3. **Given** a user, **When** they say "Tag my grocery task with shopping", **Then** the tag "shopping" is added to the matching task.
4. **Given** a user, **When** they say "Show my overdue tasks", **Then** the chatbot returns only tasks past their due date.
5. **Given** a user, **When** they say "What did I do today?", **Then** the chatbot returns today's activity log entries.

---

### User Story 9 – Deploy to Production Cloud (Priority: P1)

The system is deployed to a production cloud Kubernetes cluster using Helm charts evolved from Phase IV, with automated CI/CD and monitoring.

**Why this priority**: Cloud deployment is the core Phase V deliverable alongside the event-driven architecture. Without it, the phase objectives are not met.

**Independent Test**: Can be tested by accessing the application via the cloud-provided URL and verifying all features work end-to-end. Delivers production-grade deployment.

**Acceptance Scenarios**:

1. **Given** the Helm charts and CI/CD pipeline, **When** a commit is merged to the main branch, **Then** the application is automatically built, tested, and deployed to the cloud cluster.
2. **Given** the production deployment, **When** a user accesses the application URL, **Then** they can register, log in, and manage tasks with all Phase V features.
3. **Given** the production cluster, **When** a pod crashes, **Then** Kubernetes automatically restarts it and the system recovers without data loss.
4. **Given** the monitoring setup, **When** the system is running, **Then** logs, metrics, and health status are accessible through a centralized dashboard.
5. **Given** the local Minikube deployment, **When** the same Helm charts are used, **Then** the application deploys and runs identically to production (except for cloud-specific resources).

---

### User Story 10 – Monitor System Health (Priority: P2)

An operator can monitor the health, performance, and error rate of all system components through centralized logging and dashboards.

**Why this priority**: Observability is critical for production deployments. Without it, diagnosing issues in a distributed event-driven system is impractical.

**Independent Test**: Can be tested by verifying logs are collected, metrics are visible, and health endpoints respond. Delivers operational visibility.

**Acceptance Scenarios**:

1. **Given** the deployed system, **When** an operator queries the logging system, **Then** they can see structured logs from all services (API, frontend, event consumers, database).
2. **Given** the deployed system, **When** an operator views the metrics dashboard, **Then** they can see request rates, error rates, response times, and event processing lag.
3. **Given** a service failure, **When** it occurs, **Then** the health check endpoint reports unhealthy status and logs capture the error context.
4. **Given** the Kafka event backbone, **When** the operator checks consumer lag, **Then** they can see how far behind each consumer group is.

---

### Edge Cases

- What happens when a recurring task's next due date falls on a nonexistent date (e.g., February 30)? The system rolls forward to the next valid date (March 1 or 2).
- What happens when a user deletes a task that has a pending reminder? The reminder is cancelled and no notification is sent.
- What happens when the Kafka broker is temporarily unavailable? Events are buffered locally and retried. The system continues to accept user requests; events are delivered once Kafka recovers.
- What happens when two sessions update the same task simultaneously? Last-write-wins with the event log capturing both changes for auditability.
- What happens when a user creates a recurring task with a past start date? The system generates the first instance for the next valid future occurrence.
- How does the system handle clock skew between services for reminder scheduling? Reminders use server-side UTC timestamps; a tolerance window of 60 seconds is acceptable.
- What happens when the real-time connection drops? The client reconnects automatically and fetches current state to reconcile any missed events.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Advanced Task Features

- **FR-001**: System MUST allow users to set an optional due date (date and time) on any task.
- **FR-002**: System MUST allow users to clear or change a due date on an existing task.
- **FR-003**: System MUST visually indicate overdue tasks (past due date, not completed).
- **FR-004**: System MUST send an in-app reminder notification before a task's due date (default: 30 minutes before).
- **FR-005**: System MUST allow users to configure reminder lead time per task (options: 15 min, 30 min, 1 hour, 1 day, none).
- **FR-006**: System MUST cancel pending reminders when a task is completed or deleted.
- **FR-007**: System MUST support recurring tasks with patterns: daily, weekly (specific day), monthly (specific day), custom interval (every N days).
- **FR-008**: System MUST automatically generate the next task instance when a recurring task instance is completed.
- **FR-009**: System MUST allow users to stop recurrence on a recurring task without deleting existing instances.
- **FR-010**: System MUST support five priority levels: none (default), low, medium, high, urgent.
- **FR-011**: System MUST allow users to assign, change, or remove priority on any task.
- **FR-012**: System MUST support user-scoped tags (1–30 chars, alphanumeric plus hyphens, case-insensitive).
- **FR-013**: System MUST allow up to 10 tags per task.
- **FR-014**: System MUST provide tag auto-completion from the user's existing tags.
- **FR-015**: System MUST support full-text search on task titles.
- **FR-016**: System MUST support filtering by: status, priority, tag, due date range, overdue flag.
- **FR-017**: System MUST support sorting by: due date, priority, created date, title.
- **FR-018**: System MUST support combining search with filters (AND logic).

#### Activity / Audit Log

- **FR-019**: System MUST log every task mutation (create, update, complete, uncomplete, delete) as an immutable audit entry.
- **FR-020**: Each audit entry MUST include: timestamp, user ID, action type, task ID, changed fields with old and new values.
- **FR-021**: System MUST log system-generated actions (recurring task creation, reminder sent) with a "system" actor.
- **FR-022**: System MUST display the activity log to the user, paginated (20 entries per page), sorted newest-first.
- **FR-023**: Activity log entries MUST be durable and survive service restarts.
- **FR-023a**: Activity log entries MUST be retained for 90 days. Entries older than 90 days are eligible for automatic pruning.

#### Real-Time Synchronization

- **FR-024**: System MUST push task changes to all active sessions of the same user in real time (within 3 seconds).
- **FR-025**: System MUST push reminder notifications to all active sessions of the user.
- **FR-026**: System MUST handle client disconnection and reconnection gracefully, reconciling missed events on reconnect.

#### AI Chatbot Extension

- **FR-027**: The AI chatbot MUST support natural language commands for: setting due dates, setting priorities, adding/removing tags, creating recurring tasks, viewing overdue tasks, and querying the activity log.
- **FR-028**: The AI chatbot MUST continue to support all existing Phase III commands (add, list, complete, uncomplete, delete tasks).

#### Event Architecture

- **FR-029**: All task mutations MUST produce a durable event to the event backbone.
- **FR-030**: Events MUST be replayable for a 7-day retention window (stored with ordering guarantees per user). The PostgreSQL activity log serves as the permanent audit record beyond this window.
- **FR-031**: The system MUST tolerate event backbone unavailability by buffering events locally and retrying.
- **FR-032**: Reminder scheduling MUST be handled via a scheduled jobs mechanism (not polling).
- **FR-033**: Recurring task generation MUST be triggered by a completion event, not by a polling loop.
- **FR-034**: Real-time client notifications MUST be driven by subscribing to the event stream (not by polling the database).

#### Event Categories

The event backbone MUST support the following logical event categories:

- **Task Events**: task.created, task.updated, task.completed, task.uncompleted, task.deleted. Each event carries the full task state and the changed fields.
- **Reminder Events**: reminder.scheduled, reminder.fired, reminder.cancelled. Each event carries the task ID, user ID, and scheduled time.
- **Recurring Task Events**: recurrence.triggered, recurrence.instance-created, recurrence.stopped. Each event carries the parent task ID, recurrence pattern, and new instance ID.
- **Sync Events**: sync.task-changed (aggregated event for real-time push to clients). Carries user ID and the changed task state.
- **Audit Events**: audit.entry-created. Carries the full audit log entry for persistence.

#### Event Payload Requirements

Each event MUST contain at minimum:
- Unique event ID
- Event type (from the categories above)
- Timestamp (UTC, ISO 8601)
- User ID (owner of the affected task)
- Task ID (where applicable)
- Payload (the data specific to the event type)
- Correlation ID (to trace related events across the system)

#### Infrastructure Abstraction Requirements

The system MUST use an abstraction layer to decouple application logic from infrastructure concerns:

- **Pub/Sub Abstraction**: Application code publishes and subscribes to events through an abstraction; the underlying message broker (Kafka) is an infrastructure detail.
- **State Management Abstraction**: Where services need local state caching, the abstraction manages the state store lifecycle.
- **Secrets Abstraction**: All secrets (database credentials, API keys, JWT signing keys) MUST be retrieved through an abstraction layer, not from environment variables or config files directly.
- **Service Invocation Abstraction**: Service-to-service calls MUST go through an abstraction that handles discovery, retries, and observability.
- **Scheduled Jobs Abstraction**: Reminder scheduling MUST use a jobs abstraction that supports cron-like schedules and one-time triggers, with persistence across restarts.

#### Deployment – Local (Minikube)

- **FR-035**: The system MUST deploy to a local Minikube cluster using Helm charts evolved from Phase IV.
- **FR-036**: Local deployment MUST include all services: API, frontend, PostgreSQL, Kafka (single-node), and the abstraction layer sidecars.
- **FR-037**: Local deployment MUST be reproducible from a single Helm install command (plus image builds).
- **FR-038**: Local deployment MUST use `values-local.yaml` overrides (following Phase IV convention).

#### Deployment – Production Cloud (Oracle OKE)

- **FR-039**: The system MUST deploy to Oracle Container Engine for Kubernetes (OKE) as the production cloud target.
- **FR-040**: Production deployment MUST use managed Kafka (or equivalent streaming service) and managed PostgreSQL where available.
- **FR-041**: Production deployment MUST expose the frontend via an HTTPS endpoint with a valid domain or IP.
- **FR-042**: Production deployment MUST use Kubernetes secrets for all sensitive configuration.
- **FR-043**: Production deployment MUST survive pod restarts without data or event loss.

#### CI/CD

- **FR-044**: The CI/CD pipeline MUST be implemented using GitHub Actions.
- **FR-045**: On every push to the main branch, the pipeline MUST: build Docker images, run automated tests, push images to a container registry, and deploy to the production cluster.
- **FR-046**: The pipeline MUST fail and block deployment if any test fails.
- **FR-047**: The pipeline MUST support manual rollback to a previous version.

#### Monitoring & Logging

- **FR-048**: All services MUST emit structured logs (JSON format) to a centralized log aggregator.
- **FR-049**: All services MUST expose health check endpoints (readiness and liveness probes).
- **FR-050**: The system MUST track and expose metrics: request rate, error rate, response latency (p50, p95, p99), event processing lag, active WebSocket connections.
- **FR-051**: The monitoring setup MUST provide a dashboard accessible to operators.

### Key Entities

- **Task** (extended from Phase II): Represents a todo item. New attributes: due date, reminder lead time, priority level, recurrence pattern, recurrence parent reference. Existing attributes: ID, title, completion status, owner, timestamps.
- **Tag**: Represents a user-defined label. Attributes: ID, name (unique per user), owner. Many-to-many relationship with Task.
- **Recurrence Rule**: Represents a recurring schedule attached to a task. Attributes: pattern type (daily/weekly/monthly/custom), interval, day-of-week or day-of-month, active flag.
- **Activity Log Entry**: Represents an immutable audit record. Attributes: ID, timestamp, user ID, action type, task ID, changed fields (old/new values), actor (user or system).
- **Reminder**: Represents a scheduled notification. Attributes: ID, task ID, user ID, scheduled time, status (pending/fired/cancelled).
- **Event**: Represents a durable event in the backbone. Attributes: event ID, event type, timestamp, user ID, task ID, payload, correlation ID.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with due date, priority, and tags in a single action, completing the flow in under 10 seconds.
- **SC-002**: In-app reminders are delivered to all active user sessions within 60 seconds of the scheduled reminder time.
- **SC-003**: When a recurring task instance is completed, the next instance is visible in the user's task list within 5 seconds.
- **SC-004**: Search results return within 2 seconds for a user with up to 500 tasks.
- **SC-005**: Real-time sync delivers task changes to other sessions within 3 seconds of the mutation.
- **SC-006**: The activity log accurately captures 100% of task mutations with correct timestamps and field-level change detail.
- **SC-007**: The system recovers from a single pod restart with zero data loss and resumes normal operation within 60 seconds.
- **SC-008**: Events survive message broker downtime of up to 5 minutes through local buffering and retry.
- **SC-009**: The CI/CD pipeline completes build, test, and deploy within 15 minutes per commit.
- **SC-010**: Production deployment is accessible via a public HTTPS endpoint and all features work identically to local deployment.
- **SC-011**: The monitoring dashboard shows live metrics for all services and the event backbone consumer lag is visible.
- **SC-012**: All existing Phase II, III, and IV functionality continues to work without regression.
- **SC-013**: The local Minikube deployment deploys from a single Helm command and all pods reach running state within 5 minutes.
- **SC-014**: The AI chatbot successfully handles natural language commands for all new features (due dates, priorities, tags, recurrence, activity queries) with at least 90% intent recognition accuracy.

---

## Demo & Submission Requirements

### Demo Flow (Recommended Order)

1. **Show Kubernetes cluster**: `kubectl get all -n pakaura` on both local and production clusters.
2. **Show event infrastructure**: Demonstrate Kafka topics exist and the abstraction layer sidecars are running.
3. **Register and login**: Create a new user account and authenticate.
4. **Create task with advanced features**: Create a task with due date, high priority, and tags in a single action.
5. **Demonstrate recurring task**: Create a daily recurring task, complete it, show the next instance auto-generated.
6. **Demonstrate search and filter**: Filter tasks by priority, tag, and overdue status.
7. **Demonstrate real-time sync**: Open two browser tabs, make a change in one, show it appear in the other.
8. **Demonstrate reminder**: Show a reminder notification appearing in-app (use a short lead time for demo).
9. **Show activity log**: View the audit trail of all actions performed during the demo.
10. **AI chatbot**: Use natural language to set a due date, add a tag, and query overdue tasks.
11. **Show CI/CD**: Show the GitHub Actions pipeline (last successful run).
12. **Show monitoring**: Show the centralized logging/metrics dashboard.

### Submission Requirements

- Single GitHub repository (same as Phases I–IV).
- Phase V branch or tag clearly identified.
- README updated with Phase V deployment instructions.
- Demo video (screen recording) showing the complete demo flow above.
- Helm charts for both local and production deployment included in the repository.
- CI/CD pipeline configuration committed to the repository.

---

## Clarifications

### Session 2026-02-08

- Q: Which cloud provider for production deployment? → A: Oracle OKE (confirmed per constitution recommendation; best free tier for hackathon judging).
- Q: How long should Kafka retain events for replay? → A: 7 days. Kafka is the transport layer; PostgreSQL activity log is the permanent audit record.
- Q: What is the activity log retention policy? → A: 90 days. Entries older than 90 days are eligible for pruning. Keeps history useful while bounding storage growth.

---

## Assumptions

- Oracle OKE is the production cloud provider (per constitution recommendation). If Oracle free tier is insufficient, Azure AKS or Google GKE may be substituted with equivalent configuration.
- Reminders are in-app only (no email, SMS, or push notifications). Expanding to other channels is deferred to a future phase.
- Real-time sync uses WebSocket connections from the client to the API. The event-driven backbone powers the server side; the client protocol is a WebSocket.
- Kafka is deployed in single-broker mode for local Minikube; production may use a managed multi-broker cluster. Event retention is 7 days on all environments; PostgreSQL activity log is the permanent record.
- Dapr is the specific abstraction layer technology, providing pub/sub, state, secrets, service invocation, and jobs building blocks.
- The existing Phase II REST API surface (`/api/v1/`) is extended with new endpoints; no existing endpoints are removed or have breaking changes.
- Tag names are case-insensitive and stored in lowercase. Duplicate tag names (differing only by case) are treated as the same tag.
- The activity log is append-only and immutable. Users cannot delete or edit log entries. Entries are retained for 90 days; automatic pruning removes older entries.
- All timestamps are stored and compared in UTC. The frontend converts to the user's local timezone for display.
- The CI/CD pipeline targets the `main` branch for production deploys. Feature branches trigger build and test only (no deploy).

---

## Dependencies

- Phase IV Helm charts and Docker images (base for evolution).
- Phase II/III REST API and database schema (extended, not replaced).
- Phase III AI chatbot (extended with new tool capabilities).
- Oracle Cloud (OKE) account or equivalent cloud provider account.
- GitHub Actions (CI/CD platform).
- Container registry accessible from both CI/CD and the cloud cluster.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Kafka adds significant operational complexity to local dev | High | Medium | Use single-broker Kafka on Minikube; provide clear setup docs; Dapr abstracts broker details |
| Oracle OKE free tier resource limits may be insufficient | Medium | High | Size pods conservatively; have Azure AKS/GKE as fallback; monitor resource usage |
| Real-time WebSocket connections may not work behind some proxies/firewalls | Medium | Medium | Implement automatic fallback to long-polling if WebSocket fails |
| Event ordering guarantees across multiple Kafka partitions | Medium | Medium | Partition by user ID to guarantee per-user ordering |
| CI/CD pipeline secrets management for cloud deployment | Low | High | Use GitHub Actions encrypted secrets; never commit credentials |
| Dapr sidecar startup latency delaying pod readiness | Medium | Low | Configure appropriate init delays in health probes |

---

## Dapr Building Block Mapping

This section maps the infrastructure abstraction requirements to Dapr building blocks for planning reference:

| Abstraction Requirement | Dapr Building Block | Purpose in PakAura |
| ----------------------- | ------------------- | ------------------ |
| Pub/Sub Abstraction | Pub/Sub | Publish task events, reminder events, audit events to Kafka; subscribe to events for processing |
| State Management | State Store | Cache active reminders, consumer offsets, session state |
| Secrets Abstraction | Secrets Store | Retrieve database URLs, JWT secrets, API keys from Kubernetes secrets |
| Service Invocation | Service Invocation | API-to-consumer service calls with built-in retries and mTLS |
| Scheduled Jobs | Jobs API | Schedule reminder notifications at specific times; trigger recurring task generation |

---

## Local vs Production Deployment Requirements

| Concern | Local (Minikube) | Production (Oracle OKE) |
| ------- | ---------------- | ----------------------- |
| Kafka | Single-broker, ephemeral storage | Managed or multi-broker with persistent storage |
| PostgreSQL | Single pod with emptyDir (from Phase IV) | Managed database service or persistent volume |
| Secrets | Kubernetes secrets with local dev values | Kubernetes secrets with production values, rotated |
| Image source | Local build, `imagePullPolicy: Never` | Container registry, `imagePullPolicy: Always` |
| HTTPS / TLS | Not required (localhost) | Required with valid certificate |
| Domain | localhost via port-forward | Public domain or IP |
| Monitoring | Optional lightweight setup | Full centralized logging and metrics |
| CI/CD | Manual helm install | Automated via GitHub Actions |
| Scaling | Single replica per service | Configurable replicas per service |
| Dapr | Sidecar injection enabled | Sidecar injection enabled with production configuration |
