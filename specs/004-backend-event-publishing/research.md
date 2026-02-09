# Research: Backend Event Publishing

**Branch**: `004-backend-event-publishing` | **Date**: 2026-02-09

## R-001: Dapr Pub/Sub HTTP API for Python

**Decision**: Use `httpx.AsyncClient` to call Dapr sidecar HTTP API at `http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{pubsubname}/{topic}`

**Rationale**:
- `httpx` is already a project dependency (v0.28.1), no new packages needed
- Dapr Python SDK (`dapr`) is NOT installed and adding it would introduce a heavyweight dependency
- Direct HTTP calls to the sidecar are the simplest approach — Dapr's publish API is a single POST endpoint
- Constitution VII mandates no direct Kafka clients; httpx→Dapr sidecar satisfies this
- Non-blocking via `httpx.AsyncClient` with fire-and-forget pattern

**Alternatives considered**:
- Dapr Python SDK (`dapr-ext-grpc`/`dapr`): Heavyweight, gRPC dependency, unnecessary for simple publish
- `aiohttp`: Another async HTTP library — but httpx is already installed
- Background task queue (Celery): Over-engineered for fire-and-forget publishes

## R-002: CloudEvents 1.0 Schema Requirements

**Decision**: Use CloudEvents 1.0 structured content mode with Dapr's built-in CloudEvents wrapping

**Rationale**:
- Dapr Pub/Sub automatically wraps published data in CloudEvents envelopes when `rawPayload` is `false` (our config)
- We pass CloudEvents metadata as HTTP headers or in the JSON body
- Required attributes per CloudEvents 1.0 spec: `specversion`, `id`, `source`, `type`, `time`
- Optional attributes we include: `subject`, `datacontenttype`, `traceid` (custom extension)

**Alternatives considered**:
- Raw payload mode: Would bypass CloudEvents wrapping — violates FR-009
- Binary content mode: Metadata in headers only — harder to inspect in Kafka

## R-003: Event Publishing Error Handling Strategy

**Decision**: Fire-and-forget with structured logging. No retries at application level.

**Rationale**:
- FR-011 mandates event publishing failures MUST NOT fail the API request
- Dapr sidecar has its own retry policy for Kafka delivery
- Application-level retries would add latency to API responses
- Structured JSON logging with correlation_id enables debugging (Constitution XIII)
- If Dapr sidecar is down, the HTTP call fails fast (connection refused) — logged and moved on

**Alternatives considered**:
- Outbox pattern (write events to DB, async worker publishes): Guarantees delivery but adds DB load and complexity — overkill for this stage
- Application-level retries with backoff: Would block the API response — violates FR-011 / SC-005
- Dead letter queue: Good for consumers, not relevant for publishers

## R-004: Event Publishing Integration Approach

**Decision**: Inject event publishing at the route/handler level, after the service call succeeds, not inside `TaskService` methods

**Rationale**:
- `TaskService` methods use `db.flush()` (not commit) — the transaction isn't finalized yet inside the service
- The `get_db()` dependency handles commit/rollback in the route lifecycle
- Publishing events inside `TaskService` would fire before the transaction is committed — if the commit later fails, we'd have published invalid events
- Publishing at the route level (after the service returns and before the response is sent) ensures the DB operation succeeded
- The `get_db` dependency auto-commits on successful return, so by the time the event is published, the data is consistent
- Alternative: Use a FastAPI `BackgroundTask` to publish after the response — truly non-blocking

**Alternatives considered**:
- Inside TaskService methods: Risk of publishing before commit — rejected
- SQLAlchemy after_commit hooks: Complex, couples event logic to ORM — rejected
- Middleware-based: Too generic, can't inspect individual route payloads — rejected

## R-005: Dapr Sidecar Port Configuration

**Decision**: Use `DAPR_HTTP_PORT` environment variable (default 3500) for sidecar address

**Rationale**:
- Dapr injects `DAPR_HTTP_PORT` env var into the container when the sidecar is running
- Default port 3500 is used when running locally or when the env var is not set
- This makes the publisher work both inside Kubernetes (with Dapr) and outside (graceful failure)

**Alternatives considered**:
- Hardcode `localhost:3500`: Would work but is less flexible — rejected
- Kubernetes service discovery: Dapr sidecar is always localhost — not needed
