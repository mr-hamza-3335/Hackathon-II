# Feature Specification: Backend Event Publishing

**Feature Branch**: `004-backend-event-publishing`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Backend Event Publishing - Phase V Stage 4: Publish events for all task lifecycle actions via Dapr Pub/Sub with CloudEvents 1.0 compliance"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Lifecycle Events (Priority: P1)

As a system operator, when any task lifecycle action occurs (create, update, complete, uncomplete, delete), the system publishes a corresponding event to the `task-events` topic so that downstream services (audit, notification, recurring) can react to task changes.

**Why this priority**: Task lifecycle events are the foundation of the entire event-driven architecture. Without them, no downstream service can function. This is the core capability that unlocks all other event-driven features.

**Independent Test**: Can be fully tested by creating/updating/completing/deleting a task via the API and verifying that the corresponding event appears on the `task-events` Kafka topic via Dapr dashboard or topic consumer.

**Acceptance Scenarios**:

1. **Given** a user creates a new task via `POST /api/v1/tasks`, **When** the task is persisted to the database, **Then** a `task.created` event is published to the `task-events` topic in CloudEvents 1.0 format containing the task ID, user ID, title, and timestamp.
2. **Given** a user updates a task title via `PATCH /api/v1/tasks/{id}`, **When** the update is persisted, **Then** a `task.updated` event is published to the `task-events` topic containing the task ID, user ID, changed fields, and timestamp.
3. **Given** a user completes a task via `POST /api/v1/tasks/{id}/complete`, **When** the completion is persisted, **Then** a `task.completed` event is published to the `task-events` topic containing the task ID, user ID, and timestamp.
4. **Given** a user uncompletes a task via `POST /api/v1/tasks/{id}/uncomplete`, **When** the change is persisted, **Then** a `task.uncompleted` event is published to the `task-events` topic.
5. **Given** a user deletes a task via `DELETE /api/v1/tasks/{id}`, **When** the deletion is persisted, **Then** a `task.deleted` event is published to the `task-events` topic containing the task ID and user ID.
6. **Given** the event publishing service is unavailable, **When** a user performs any task action, **Then** the API request completes successfully and the failure is logged — the user is never impacted by event publishing failures.

---

### User Story 2 - Real-Time Sync Events (Priority: P2)

As a system operator, when a task is mutated, the system publishes a lightweight sync event to the `task-updates` topic so that the WebSocket gateway can push real-time updates to connected clients.

**Why this priority**: Real-time sync events enable live UI updates across multiple sessions/devices. They are published alongside lifecycle events but to a separate topic, keeping the broadcast channel lightweight.

**Independent Test**: Can be tested by performing a task mutation and verifying a sync event appears on the `task-updates` topic with minimal payload (task ID, action type, user ID).

**Acceptance Scenarios**:

1. **Given** any task mutation occurs (create, update, complete, uncomplete, delete), **When** the change is persisted, **Then** a sync event is published to the `task-updates` topic containing the task ID, action type, and user ID.
2. **Given** multiple task mutations occur rapidly, **When** each is persisted, **Then** each produces its own sync event in order.

---

### User Story 3 - Reminder Events (Priority: P3)

As a system operator, when a task with a due date is created or its due date is updated, the system publishes a reminder event to the `reminders` topic so that the notification service can schedule or reschedule reminders.

**Why this priority**: Reminder events depend on a due-date field. Since the current Task model does not include a due date, this story establishes the event pathway and will publish reminder events when the due-date feature is available. For now, the publishing infrastructure is created but only fires when a due date is present.

**Independent Test**: Can be tested by setting a due date on a task (once the field exists) and verifying a reminder event appears on the `reminders` topic.

**Acceptance Scenarios**:

1. **Given** a task is created with a due date, **When** the task is persisted, **Then** a `reminder.scheduled` event is published to the `reminders` topic containing the task ID, user ID, and due date.
2. **Given** a task's due date is updated, **When** the update is persisted, **Then** a `reminder.rescheduled` event is published to the `reminders` topic containing the task ID and the new due date.
3. **Given** a task without a due date is created or updated, **When** the task is persisted, **Then** no reminder event is published.

---

### Edge Cases

- What happens when the Dapr sidecar is not available? The event publish call fails gracefully; the API request still succeeds, and the failure is logged with full context.
- What happens when a task is updated but no fields actually changed? The system still publishes an update event (idempotent consumers handle deduplication).
- What happens when multiple events need to be published for a single action (e.g., task.completed + sync)? Each event is published independently; a failure in one does not prevent the other.
- What happens during high load with many concurrent task operations? Events are published asynchronously without blocking the HTTP response, so API latency is unaffected.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST publish a `task.created` event to the `task-events` topic when a new task is created
- **FR-002**: System MUST publish a `task.updated` event to the `task-events` topic when a task's title is modified
- **FR-003**: System MUST publish a `task.completed` event to the `task-events` topic when a task is marked complete
- **FR-004**: System MUST publish a `task.uncompleted` event to the `task-events` topic when a task is marked incomplete
- **FR-005**: System MUST publish a `task.deleted` event to the `task-events` topic when a task is deleted
- **FR-006**: System MUST publish a sync event to the `task-updates` topic for every task mutation (create, update, complete, uncomplete, delete)
- **FR-007**: System MUST publish a `reminder.scheduled` event to the `reminders` topic when a task with a due date is created (future-ready — fires only when due date field exists)
- **FR-008**: System MUST publish a `reminder.rescheduled` event to the `reminders` topic when a task's due date is modified (future-ready)
- **FR-009**: All published events MUST conform to the CloudEvents 1.0 specification, including required attributes: `specversion`, `id`, `source`, `type`, `time`
- **FR-010**: All events MUST include `subject` (task ID), `datacontenttype` (`application/json`), and a structured `data` payload
- **FR-011**: Event publishing MUST be non-blocking — failures MUST NOT cause the API request to fail or return an error to the user
- **FR-012**: All event publishing failures MUST be logged with sufficient context for debugging (event type, task ID, error details)
- **FR-013**: Events MUST be published via the Dapr Pub/Sub abstraction layer (pubsub component name: `pubsub-kafka`) — no direct Kafka client usage
- **FR-014**: Each event MUST include a correlation ID for end-to-end traceability across services
- **FR-015**: Existing task CRUD API behavior MUST remain unchanged — same request/response contracts, same status codes, same error handling

### Key Entities

- **TaskEvent**: An event representing a task lifecycle action. Contains event metadata (type, source, timestamp, correlation ID) and task data (task ID, user ID, title, completed status, changed fields).
- **SyncEvent**: A lightweight event for real-time broadcasting. Contains the task ID, action type (created/updated/completed/uncompleted/deleted), and user ID.
- **ReminderEvent**: An event for reminder scheduling. Contains the task ID, user ID, due date, and reminder action type (scheduled/rescheduled).

## Assumptions

- The Dapr sidecar is available at `http://localhost:3500` (standard Dapr sidecar port) when running in Kubernetes.
- The `pubsub-kafka` Dapr component is already configured (completed in Phase V Stage 3).
- The three Kafka topics (`task-events`, `reminders`, `task-updates`) are already created (completed in Phase V Stage 3).
- The Task model does not currently have a `due_date` field; reminder events are infrastructure-ready but will only fire when this field is added in a future phase.
- Event publishing uses HTTP calls to the Dapr sidecar API (`/v1.0/publish/{pubsubname}/{topic}`).
- Events are fire-and-forget — no delivery guarantees beyond Dapr/Kafka's built-in mechanisms.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of task lifecycle actions (create, update, complete, uncomplete, delete) produce corresponding events on the `task-events` topic
- **SC-002**: 100% of task mutations produce a sync event on the `task-updates` topic
- **SC-003**: All published events pass CloudEvents 1.0 schema validation (specversion, id, source, type, time present)
- **SC-004**: Event publishing failures do not increase API error rates — existing API endpoints maintain their current success rate
- **SC-005**: Event publishing adds less than 50ms of overhead to API response times (non-blocking, async)
- **SC-006**: All existing task CRUD API tests continue to pass without modification
