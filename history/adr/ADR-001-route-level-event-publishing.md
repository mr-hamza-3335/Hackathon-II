# ADR-001: Route-Level Event Publishing for Backend Events

- **Status:** Accepted
- **Date:** 2026-02-09
- **Feature:** 004-backend-event-publishing
- **Context:** Phase V introduces an event-driven architecture where all task lifecycle actions must produce CloudEvents to Kafka topics via Dapr Pub/Sub. The critical design question is WHERE in the request lifecycle to inject event publishing calls — at the service layer, the route/handler layer, or via middleware.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Yes — determines how events correlate with DB transactions across all services
     2) Alternatives: Yes — three viable options with distinct tradeoffs
     3) Scope: Yes — affects every task mutation endpoint and future event-producing services
-->

## Decision

**Publish events at the route/handler layer**, after the `TaskService` method returns successfully and before the HTTP response is sent. Each route handler explicitly calls `EventPublisher.publish_task_event()` and `EventPublisher.publish_sync_event()` after the service operation completes.

**Why not inside TaskService:**
- `TaskService` methods call `db.flush()` (not `db.commit()`). The transaction is finalized by the `get_db()` dependency AFTER the handler returns.
- Publishing inside the service would fire events BEFORE the DB transaction commits. If the commit fails (constraint violation, connection drop), we'd have published events for data that was rolled back — a ghost event.
- Separating concerns: the service layer handles business logic and data access; event publishing is an infrastructure concern.

**Why not middleware:**
- Middleware operates at the HTTP request/response boundary with no knowledge of which operation occurred or what data changed.
- Event payloads require operation-specific data (task ID, action type, changed fields) that middleware cannot inspect without parsing route parameters and response bodies — fragile and error-prone.
- Different routes publish different event types; a generic middleware would require a complex routing table that duplicates what the handlers already know.

## Consequences

### Positive

- **DB commit safety**: Events only fire after the service confirms the operation succeeded. Even though the commit happens slightly later (in the dependency cleanup), `flush()` validates constraints — if `flush()` succeeds, the commit will almost certainly succeed.
- **Explicit control**: Each handler declares exactly which events it produces. No hidden side effects, no magic. A developer reading `create_task()` can see the full picture: validate → persist → publish → respond.
- **Easy observability**: Event publishing calls are visible in the handler, making it trivial to trace which endpoints produce which events. Correlation IDs are generated once per request and flow through all events.
- **Independent failure handling**: Each event publish is wrapped in its own try/except. A failure in `task-events` doesn't prevent the `task-updates` publish. The API response is never affected.
- **Testable**: Handlers can be unit-tested by mocking `EventPublisher`. No need to mock deep inside the service layer.

### Negative

- **Slight duplication**: Each handler has 2-3 lines of event publishing code. Five handlers × ~3 lines = ~15 lines of repeated pattern. Acceptable for explicitness.
- **MCP layer requires separate integration**: `mcp_server/task_operations.py` bypasses the route layer (uses direct asyncpg), so event publishing must be added there separately — same pattern, different call sites.
- **Not transactionally coupled**: There is a tiny window where the DB commits but the event publish fails (network issue). This is accepted as a deliberate tradeoff — the spec mandates fire-and-forget (FR-011). Kafka consumers must be idempotent.
- **Future handlers must remember**: Any new task mutation endpoint added in the future must explicitly include event publishing calls. This is mitigated by the spec-driven workflow — new endpoints will be spec'd with event requirements.

## Alternatives Considered

### Alternative 1: Service-Level Publishing (inside TaskService)

Place event publishing inside `TaskService.create()`, `TaskService.update()`, etc.

**Why rejected:**
- `TaskService` uses `db.flush()`, not `db.commit()`. Events would fire before the transaction is finalized.
- If the transaction rollback occurs after flush (e.g., serialization failure), ghost events would be published for non-existent data.
- Couples business logic (task CRUD) with infrastructure concerns (event publishing).
- Would require injecting an HTTP client into the service layer, which currently only depends on the DB session.

### Alternative 2: Middleware-Based Publishing

Use FastAPI middleware to intercept responses and publish events based on route + status code.

**Why rejected:**
- Middleware lacks context about what operation was performed and what data changed.
- Would need to parse response bodies to extract task data — fragile, breaks if response format changes.
- Different routes need different event types — the middleware would need a complex mapping table.
- Error handling becomes opaque: failures in event publishing could interfere with response delivery.
- Cannot handle the MCP layer (which doesn't go through FastAPI middleware).

### Alternative 3: SQLAlchemy Event Hooks (after_commit)

Use SQLAlchemy's `after_commit` session event to trigger event publishing.

**Why rejected:**
- SQLAlchemy hooks run in the session context, which may not have an active event loop for async HTTP calls.
- Tight coupling between ORM and event infrastructure.
- Difficult to test — requires a live database session.
- Cannot distinguish between different mutation types (create vs. update vs. delete) without inspecting the session's dirty/new/deleted sets.

## References

- Feature Spec: [specs/004-backend-event-publishing/spec.md](../../specs/004-backend-event-publishing/spec.md)
- Implementation Plan: [specs/004-backend-event-publishing/plan.md](../../specs/004-backend-event-publishing/plan.md)
- Research: [specs/004-backend-event-publishing/research.md](../../specs/004-backend-event-publishing/research.md) — R-004
- Related ADRs: None (first ADR)
- Constitution: Principles VII (no direct Kafka), VIII (all async via Dapr), XIV (every service event-driven)
