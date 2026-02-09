# Tasks: Backend Event Publishing

**Input**: Design documents from `/specs/004-backend-event-publishing/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Event publishing infrastructure that ALL user stories depend on

**CRITICAL**: No event publishing can work until this phase is complete

- [x] T-010 [P] Define CloudEvents schema models in `api/src/events/schemas.py`
  - **Preconditions**: plan.md §1 (CloudEvents schema), data-model.md (event payloads)
  - **Files to create**: `api/src/events/schemas.py`
  - **Expected output**: Pydantic models: `CloudEvent`, `TaskEventData`, `SyncEventData`, `ReminderEventData`
  - **Validation**: Models can be instantiated and serialized to JSON matching data-model.md samples
  - **FR refs**: FR-009, FR-010, FR-014

- [x] T-011 Implement Dapr Pub/Sub publisher helper in `api/src/events/publisher.py`
  - **Preconditions**: T-010 complete, plan.md §3 (publish flow), §4.2 (publisher design), contracts/dapr-publish-api.md
  - **Files to create**: `api/src/events/publisher.py`
  - **Expected output**: `EventPublisher` class with methods: `publish_task_event()`, `publish_sync_event()`, `publish_reminder_event()`, `publish_task_event_from_dict()`, `_publish()`, `_build_cloud_event()`
  - **Validation**: Publisher correctly builds CloudEvents, calls Dapr sidecar HTTP API, handles all error cases (disabled, timeout, connection error, HTTP error)
  - **FR refs**: FR-011, FR-012, FR-013

- [x] T-012 [P] Create events module init in `api/src/events/__init__.py`
  - **Preconditions**: T-010 started (file structure known)
  - **Files to create**: `api/src/events/__init__.py`
  - **Expected output**: Module exports `EventPublisher`, `get_event_publisher()`
  - **Validation**: `from src.events import get_event_publisher` works
  - **FR refs**: N/A (infrastructure)

- [x] T-013 [P] Add Dapr configuration settings to `api/src/config.py`
  - **Preconditions**: plan.md §8.1 (configuration)
  - **Files to modify**: `api/src/config.py`
  - **Expected output**: New settings: `dapr_enabled` (bool, default False), `dapr_http_port` (int, default 3500), `dapr_pubsub_name` (str, default "pubsub-kafka"), `dapr_publish_timeout` (float, default 2.0)
  - **Validation**: Settings load from env vars; defaults work without .env changes
  - **FR refs**: FR-013

**Checkpoint**: Event publishing module exists and can build + publish CloudEvents. Not yet integrated with any route.

---

## Phase 2: User Story 1 — Task Lifecycle Events (Priority: P1)

**Goal**: Every task CRUD action publishes a `task.*` event to the `task-events` topic

**Independent Test**: Create/update/complete/uncomplete/delete a task → verify corresponding event on `task-events` topic

### Implementation

- [x] T-014 Integrate event publishing into task CRUD routes in `api/src/routes/tasks.py`
  - **Preconditions**: T-010, T-011, T-012, T-013 complete
  - **Files to modify**: `api/src/routes/tasks.py`
  - **Expected output**: Each of the 5 route handlers (create, update, delete, complete, uncomplete) calls `publisher.publish_task_event()` after the service call succeeds
  - **Validation**:
    - `create_task()` publishes `task.created` with task data
    - `update_task()` publishes `task.updated` with changed fields
    - `delete_task()` publishes `task.deleted` with task ID and user ID
    - `complete_task()` publishes `task.completed`
    - `uncomplete_task()` publishes `task.uncompleted`
    - ALL existing API behavior unchanged (same responses, same status codes)
  - **FR refs**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-011, FR-015

- [x] T-015 Add logging and tracing metadata to event publisher in `api/src/events/publisher.py`
  - **Preconditions**: T-011 complete
  - **Files to modify**: `api/src/events/publisher.py`
  - **Expected output**: Structured JSON logging for all publish outcomes (success, failure, disabled). Each log includes: event_type, topic, task_id, user_id, correlation_id, dapr_status (if applicable)
  - **Validation**: Logs appear in structured format with all required fields; no unstructured print statements
  - **FR refs**: FR-012, FR-014

- [x] T-016 Add safety guards — publish failures don't break API in `api/src/events/publisher.py`
  - **Preconditions**: T-011, T-015 complete
  - **Files to modify**: `api/src/events/publisher.py`
  - **Expected output**: All exceptions in `_publish()` are caught and logged. The method NEVER raises. Timeout set to 2 seconds. Connection errors logged at WARNING. HTTP errors logged at ERROR.
  - **Validation**:
    - When Dapr sidecar is down: API request succeeds, WARNING logged
    - When publish times out: API request succeeds, WARNING logged
    - When Dapr returns non-204: API request succeeds, ERROR logged
    - When DAPR_ENABLED=false: No HTTP call made, DEBUG logged
  - **FR refs**: FR-011, FR-012

**Checkpoint**: All 5 task lifecycle events publish to `task-events` topic. API behavior unchanged.

---

## Phase 3: User Story 2 — Real-Time Sync Events (Priority: P2)

**Goal**: Every task mutation also publishes a lightweight sync event to `task-updates` topic

**Independent Test**: Mutate a task → verify sync event on `task-updates` topic

### Implementation

- [x] T-017 Add sync event publishing to task CRUD routes in `api/src/routes/tasks.py`
  - **Preconditions**: T-014 complete (lifecycle events already integrated)
  - **Files to modify**: `api/src/routes/tasks.py`
  - **Expected output**: Each of the 5 route handlers additionally calls `publisher.publish_sync_event()` after the lifecycle event publish
  - **Validation**:
    - Each task mutation produces BOTH a lifecycle event (task-events) AND a sync event (task-updates)
    - Sync events contain: task_id, user_id, action, timestamp (lightweight)
    - Failure in sync publish doesn't affect lifecycle publish or API response
  - **FR refs**: FR-006

**Checkpoint**: All task mutations produce both lifecycle AND sync events on separate topics.

---

## Phase 4: User Story 3 — Reminder Events (Priority: P3)

**Goal**: Reminder event infrastructure ready for when `due_date` field is added to Task model

**Independent Test**: Call `publish_reminder_event()` directly → verify event on `reminders` topic

### Implementation

- [x] T-018 Verify reminder event schema and publisher method in `api/src/events/schemas.py` and `api/src/events/publisher.py`
  - **Preconditions**: T-010, T-011 complete (reminder schemas and method already created in foundational phase)
  - **Files to verify**: `api/src/events/schemas.py`, `api/src/events/publisher.py`
  - **Expected output**: `ReminderEventData` model exists with fields: task_id, user_id, action, due_date, timestamp. `publish_reminder_event()` method exists and publishes to `reminders` topic. No route integration yet (Task model lacks due_date).
  - **Validation**: Method can be called programmatically and produces a valid CloudEvent on the `reminders` topic
  - **FR refs**: FR-007, FR-008

**Checkpoint**: Reminder infrastructure is built. Will activate when due_date field is added in a future phase.

---

## Phase 5: MCP Server Integration & Polish

**Purpose**: Extend event publishing to the MCP layer and finalize

- [x] T-019 Integrate event publishing into MCP task operations in `api/src/mcp_server/task_operations.py`
  - **Preconditions**: T-014, T-017 complete (patterns established in routes)
  - **Files to modify**: `api/src/mcp_server/task_operations.py`
  - **Expected output**: Each of the 6 MCP methods (add_task, update_task, complete_task, uncomplete_task, delete_task, clear_completed) publishes both lifecycle and sync events after successful DB operations
  - **Validation**:
    - MCP operations produce same events as route handlers
    - `clear_completed()` publishes one `task.deleted` + sync per deleted task
    - Failures don't break MCP operations
  - **FR refs**: FR-001–006, FR-011

- [x] T-020 [P] Update Helm values for Dapr event publishing config
  - **Preconditions**: T-013 complete (config settings defined)
  - **Files to modify**: `infra/helm/pakaura/values.yaml`, `infra/helm/pakaura/values-local.yaml`
  - **Expected output**: API environment section includes `DAPR_ENABLED: "true"` for Kubernetes deployments
  - **Validation**: Helm template renders correct env vars for the API container
  - **FR refs**: FR-013

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — start immediately
  - T-010, T-012, T-013 can run in parallel [P]
  - T-011 depends on T-010 (needs schema models)
- **Phase 2 (US1 Lifecycle)**: Depends on ALL of Phase 1
  - T-014 first, then T-015 and T-016
- **Phase 3 (US2 Sync)**: Depends on T-014 from Phase 2
- **Phase 4 (US3 Reminders)**: Depends on Phase 1 only (verification task)
- **Phase 5 (MCP + Polish)**: Depends on Phase 2 and Phase 3

### Critical Path

```
T-010 → T-011 → T-014 → T-015 → T-016 → T-017 → T-019
  ↑        ↑
T-012 (P)  T-013 (P)
```

### Parallel Opportunities

```
Phase 1: T-010 ∥ T-012 ∥ T-013  (3 tasks in parallel)
Phase 2: T-015 ∥ T-016           (after T-014)
Phase 5: T-019 ∥ T-020           (after Phase 3)
Phase 4: T-018 can run anytime after Phase 1
```

---

## Notes

- All task IDs (T-010 through T-020) MUST be referenced in code comments and commit messages
- No new pip dependencies required — httpx is already installed
- DAPR_ENABLED defaults to false — existing local dev workflow unchanged
- Reminder events (T-018) are infrastructure-only; no route integration until due_date field exists
