<!--
  SYNC IMPACT REPORT
  ==================
  Version change: 1.0.1 → 1.1.0 (MINOR - Phase V principles added)

  Modified principles:
  - Phase V section: Expanded from 4 lines to full principle set with 8 non-negotiable rules

  Added sections:
  - Phase V Non-Negotiable Principles (8 principles: VII–XIV)
  - Phase V Compliance Checklist
  - Phase V Violation Examples

  Removed sections: N/A

  Rationale:
  - Phase V introduces event-driven microservices architecture requiring strict governance
  - Dapr abstraction layer mandate prevents infrastructure lock-in and enforces clean boundaries
  - Cloud-agnostic principle ensures portability across OKE/AKS/GKE
  - Observability mandate prevents "deploy and pray" anti-pattern in distributed systems
  - All 8 principles trace directly to spec FR requirements and constitution Phase V mandate

  Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (no impact)
  - .specify/templates/spec-template.md ✅ (no impact)
  - .specify/templates/tasks-template.md ✅ (no impact)

  Follow-up TODOs:
  - All Phase V code reviews MUST check against the new compliance checklist
-->

# Evolution of Todo Constitution

## Hackathon II – AI / Spec-Driven Development

## Purpose

This constitution defines the **rules, quality standards, and boundaries**
for the Hackathon II "Evolution of Todo" project.

All development MUST follow **Spec-Driven Development**.
Claude Code and the developer are both REQUIRED to follow this constitution
across all five phases of the hackathon.

Manual coding is strictly prohibited.

## Core Principles

### I. Spec-Driven Development Only

- No code may be written or edited manually.
- Every feature MUST be defined in a markdown spec before implementation.
- If behavior is unclear or incorrect, the spec MUST be updated first.

### II. Single Repository Rule

- The entire project MUST live in a single GitHub repository.
- Separate repositories per phase are NOT allowed.
- Project history and evolution must remain visible.

### III. Evolution Over Rewrite

- Each phase MUST extend the previous phase.
- Existing functionality MUST NOT be rewritten or discarded unless explicitly stated in the spec.
- Backward compatibility MUST be preserved whenever possible.

### IV. Single Source of Truth

- All requirements live exclusively in `/specs/**`.
- README files, comments, or verbal instructions are NOT authoritative.
- Code behavior MUST always match the specs.

### V. Clean Architecture

- Clear separation of concerns is required:
  - `/specs` → requirements
  - `/api` → core API service
  - `/services` → event-processing microservices
  - `/frontend` → UI
  - `/infra` → Helm charts, Dockerfiles, Kubernetes manifests
- Naming conventions MUST be consistent and meaningful.

### VI. Professional Quality Bar

- Code MUST be readable, maintainable, and production-grade.
- Unnecessary abstractions and over-engineering are prohibited.
- Best practices for each technology stack MUST be followed.

---

## Phase V Non-Negotiable Principles

The following principles are **mandatory and unconditional** for all Phase V development. They define architectural constraints, not features. No task, shortcut, or deadline justifies violating them.

### VII. No Direct Kafka Client Usage in Application Code

- Application code MUST NEVER import, instantiate, or call Kafka client libraries (`kafka-python`, `confluent-kafka`, `aiokafka`, or any Kafka SDK) directly.
- All event publishing MUST go through the Dapr Pub/Sub HTTP API.
- All event subscribing MUST be handled via Dapr subscription declarations and HTTP callback routes.
- **Why**: Kafka is an infrastructure detail. Application logic must not couple to a specific message broker. Replacing Kafka with another broker (Redis Streams, RabbitMQ, cloud-native streaming) MUST require zero application code changes.
- **Violation example**: `from kafka import KafkaProducer` in any Python service file.
- **Correct pattern**: `httpx.post("http://localhost:3500/v1.0/publish/pubsub-kafka/task-events", json=event)` or Dapr SDK `DaprClient().publish_event()`.
- **Spec basis**: Infrastructure Abstraction Requirements — Pub/Sub Abstraction.

### VIII. All Asynchronous Communication Via Dapr

- All inter-service asynchronous communication MUST flow through Dapr building blocks:
  - **Pub/Sub** for event publishing and subscription.
  - **Service Invocation** for synchronous service-to-service calls.
  - **State Store** for ephemeral state management.
  - **Secrets Store** for retrieving sensitive configuration.
  - **Jobs API** for scheduled and one-time triggers.
- No service may bypass Dapr to communicate with another service directly (no raw HTTP to internal service IPs, no shared database writes between services).
- **Why**: Dapr provides service discovery, retries, mTLS, distributed tracing, and observability as infrastructure concerns. Bypassing it creates blind spots and fragile coupling.
- **Violation example**: `httpx.post("http://recurring-service:8001/events/task-completed", ...)` (direct HTTP to service).
- **Correct pattern**: `httpx.post("http://localhost:3500/v1.0/invoke/recurring-service/method/events/task-completed", ...)` (via Dapr sidecar).
- **Spec basis**: Infrastructure Abstraction Requirements — all five building blocks.

### IX. No Secrets Hard-Coded

- No secret, credential, API key, token, password, or connection string may appear as a literal value in any source file, configuration file, Dockerfile, Helm template, or CI/CD workflow.
- All secrets MUST be retrieved at runtime through:
  - **Dapr Secrets Store** (primary, for application services), or
  - **Kubernetes Secrets** (for Helm-injected environment variables), or
  - **GitHub Actions encrypted secrets** (for CI/CD pipelines).
- `.env` files with real credentials MUST NEVER be committed. `.env.example` with placeholder values is acceptable.
- **Why**: Leaked secrets are irreversible. A single committed credential compromises the entire system.
- **Violation example**: `DATABASE_URL = "postgresql://user:password@host/db"` in any Python file.
- **Correct pattern**: Read from Dapr secrets API or Kubernetes secret-injected environment variable at runtime.
- **Spec basis**: FR-042 (Kubernetes secrets for production), Infrastructure Abstraction Requirements — Secrets Abstraction.

### X. Kubernetes-First Design

- Every service MUST be designed to run in Kubernetes. No service may assume it runs on bare metal, a VM, or a specific OS.
- All services MUST:
  - Be containerized via Docker with a minimal base image.
  - Define resource requests and limits (memory, CPU).
  - Expose readiness and liveness probes (FR-049).
  - Support graceful shutdown (handle SIGTERM).
  - Be stateless (all persistent state in PostgreSQL or Kafka; ephemeral state in Dapr State Store).
- Deployment MUST use Helm charts exclusively. No `kubectl apply -f` for application workloads.
- Configuration MUST be externalized (ConfigMaps, Secrets, Helm values). No config in Docker images.
- **Why**: Kubernetes is the deployment target for both local (Minikube) and production (OKE). Designing outside Kubernetes creates deployment friction and environment parity issues.
- **Violation example**: A service that writes to a local file for state persistence.
- **Correct pattern**: Use Dapr State Store for ephemeral state; PostgreSQL for persistent data.
- **Spec basis**: FR-035–043 (deployment requirements), FR-049 (health probes).

### XI. Cloud-Agnostic Architecture

- The application architecture MUST NOT depend on any single cloud provider's proprietary services in a way that prevents migration.
- Infrastructure dependencies MUST be abstracted through Dapr or standard Kubernetes APIs:
  - Message broker → Dapr Pub/Sub (swappable between Kafka, Azure Event Hubs, GCP Pub/Sub).
  - Database → Standard PostgreSQL (deployable on any cloud or self-hosted).
  - Secrets → Dapr Secrets Store backed by Kubernetes Secrets (portable).
  - State → Dapr State Store (swappable between Redis, in-memory, cloud-native).
- Cloud-specific configuration (registry URLs, managed service endpoints, TLS certs) MUST live exclusively in `values-production.yaml`, never in application code.
- Switching from Oracle OKE to Azure AKS or Google GKE MUST require only:
  1. A new `values-production.yaml` (or override file).
  2. Updated CI/CD secrets.
  3. Zero application code changes.
- **Why**: The constitution permits Oracle OKE, Azure AKS, or Google GKE. The architecture must support any of them without refactoring.
- **Violation example**: Importing `oci-sdk` in application code; using Oracle-specific APIs in service logic.
- **Correct pattern**: All cloud-specific details in Helm values; application code talks only to Dapr and PostgreSQL.
- **Spec basis**: Spec Assumptions (OKE with AKS/GKE fallback), Constitution Phase V (Any One cloud provider).

### XII. No Manual Coding Outside Spec-Kit Workflow

- This principle reinforces Core Principle I with Phase V specifics.
- All Phase V features, services, and infrastructure MUST be:
  1. Defined in `specs/003-phase-v-cloud-deployment/spec.md` (already done).
  2. Designed in `specs/003-phase-v-cloud-deployment/plan.md` (already done).
  3. Broken into tasks in `specs/003-phase-v-cloud-deployment/tasks.md` (already done).
  4. Implemented by Claude Code following the task definitions.
  5. Recorded with a PHR in `history/prompts/003-phase-v-cloud-deployment/`.
- No code change may be made without a corresponding task reference (T-###).
- No architectural decision may be made without being traceable to the plan.
- **Why**: Spec-Driven Development is the hackathon's evaluation criterion. Undocumented changes are invisible to evaluators and create drift between spec and implementation.
- **Violation example**: Adding a new endpoint without a task reference or PHR.
- **Correct pattern**: Reference T-### in commit messages and PHRs; every file change traces to a task.
- **Spec basis**: Constitution Core Principle I, CLAUDE.md Execution Contract.

### XIII. Observability Is Mandatory

- Every service MUST implement all three pillars of observability:
  1. **Structured Logging**: JSON-formatted logs with timestamp, level, service name, and correlation_id. No unstructured `print()` statements in production code.
  2. **Metrics**: Prometheus-compatible `/metrics` endpoint exposing request rate, error rate, latency histograms (p50/p95/p99), and service-specific gauges.
  3. **Health Probes**: `/health/ready` (readiness — dependencies up) and `/health/live` (liveness — process running).
- The monitoring stack (Prometheus + Grafana + Loki) MUST be deployed alongside application services.
- A service that cannot be observed MUST NOT be deployed to production.
- **Why**: In a distributed event-driven system with 6 services, Kafka, and Dapr sidecars, diagnosing issues without observability is impossible. This is not a nice-to-have; it is a production requirement.
- **Violation example**: A service with `print("error occurred")` instead of structured JSON logging.
- **Correct pattern**: `logger.error("Task creation failed", extra={"task_id": id, "user_id": uid, "correlation_id": cid})` → JSON output.
- **Spec basis**: FR-048 (structured logs), FR-049 (health probes), FR-050 (metrics), FR-051 (dashboard).

### XIV. Every Service Must Be Event-Driven

- Every backend service (API, Notification, Recurring, Audit, WebSocket Gateway) MUST participate in the event-driven architecture:
  - **Producers** MUST publish CloudEvents v1.0 envelopes to Kafka topics via Dapr Pub/Sub after every state-changing operation.
  - **Consumers** MUST subscribe to relevant topics via Dapr subscriptions and process events via HTTP callback routes.
- No service may rely on polling a database or another service for state changes.
- No service may write directly to another service's database. All cross-service communication flows through events or Dapr Service Invocation.
- Events MUST be:
  - **Durable**: Survive broker and service restarts (Kafka 7-day retention).
  - **Ordered**: Per-user ordering guaranteed via `user_id` partition key.
  - **Idempotent**: Consumers MUST handle duplicate events gracefully using event ID deduplication.
  - **Replayable**: Any consumer can be restarted and replay events from a known offset.
- **Why**: The constitution mandates Kafka for four use cases (reminders, recurring tasks, audit logs, real-time sync). Event-driven design is not optional — it is the architectural foundation of Phase V.
- **Violation example**: Recurring Service queries the tasks database every 60 seconds looking for completed recurring tasks.
- **Correct pattern**: Recurring Service subscribes to `task.completed` events on the `task-events` topic and reacts to each completion event.
- **Spec basis**: FR-029–034 (event architecture), Constitution Phase V (Kafka MUST be used).

---

## Phase V Compliance Checklist

Every pull request, code review, and task completion MUST verify against this checklist:

| # | Check | Principle |
|---|-------|-----------|
| 1 | No Kafka client library imports in application code | VII |
| 2 | All inter-service calls go through Dapr sidecar (localhost:3500) | VIII |
| 3 | No literal secrets in source files, configs, or Dockerfiles | IX |
| 4 | Service has Dockerfile, resource limits, health probes, graceful shutdown | X |
| 5 | No cloud-provider-specific imports in application code | XI |
| 6 | Change references a task ID (T-###) and has/will have a PHR | XII |
| 7 | Service emits JSON logs, exposes /metrics, has /health/ready and /health/live | XIII |
| 8 | State changes produce CloudEvents; no database polling for state changes | XIV |

If any check fails, the change MUST be corrected before merge.

---

## Phase Constitutions

### Phase I – Console Todo Application

**Scope**: Command-line Todo application written in Python with in-memory storage only.

**Functional Requirements**:
- The application MUST support: Add task, Update task, Delete task, List tasks, Mark task complete/incomplete.

**Technical Requirements**:
- Python 3.13+
- Clean project structure
- No persistence between runs

**Restrictions**:
- No external databases
- No web UI
- No authentication

### Phase II – Full-Stack Web Application

**Scope**: Transform the console app into a multi-user web application.

**Architecture**:
- Frontend: Next.js (App Router)
- Backend: FastAPI (Python)
- Database: PostgreSQL (Neon Serverless)
- Authentication: Better Auth with JWT

**Security Rules**:
- All API endpoints MUST require authentication.
- JWT tokens MUST be verified on every request.
- Users may ONLY access their own tasks.

**Data Rules**:
- Tasks MUST be associated with a user ID.
- All queries MUST be filtered by authenticated user.

### Phase III – AI-Powered Todo Chatbot

**Scope**: Introduce a conversational AI interface for managing todos.

**AI Behavior Rules**:
- The chatbot MUST interpret natural language commands.
- The chatbot MUST call existing Phase II REST API endpoints to manage tasks.
- The chatbot MUST NOT directly manipulate the database.

**REST API Endpoints**: POST /api/v1/tasks, GET /api/v1/tasks, PATCH /api/v1/tasks/{id}, DELETE /api/v1/tasks/{id}, POST /api/v1/tasks/{id}/complete, POST /api/v1/tasks/{id}/uncomplete

**Stateless Design**:
- Each request MUST be handled independently.
- Server-side conversation memory is NOT allowed.

### Phase IV – Local Kubernetes Deployment

**Scope**: Deploy the application locally using Kubernetes.

**Infrastructure Rules**:
- All services MUST be containerized using Docker.
- Kubernetes deployment MUST use Minikube and Helm charts.

**AIOps**:
- Use kubectl-ai and kagent where applicable.
- Deployment MUST be reproducible.

### Phase V – Advanced Cloud Deployment

**Scope**: Deploy the system to a cloud Kubernetes provider with event-driven microservices architecture.

**Cloud Providers** (Any One): Oracle Cloud OKE (Recommended), Azure AKS, Google GKE.

**Event-Driven Architecture**:
- Kafka MUST be used for: Task reminders, Recurring tasks, Activity/audit logs, Real-time synchronization.
- All four Kafka use cases are mandatory. Omitting any one is a constitution violation.

**Reliability Rules**:
- System MUST tolerate restarts without data or event loss.
- Events MUST be durable (7-day Kafka retention) and replayable.
- PostgreSQL activity log MUST serve as the permanent audit record beyond the 7-day window.

**Infrastructure Abstraction**:
- Dapr MUST be the abstraction layer for: Pub/Sub, State, Secrets, Service Invocation, and Scheduled Jobs.
- Application code MUST NOT directly depend on Kafka, Redis, or any infrastructure client library.

**Non-Negotiable Principles** (VII–XIV above apply exclusively and completely to Phase V):
- VII: No direct Kafka clients
- VIII: All async via Dapr
- IX: No hard-coded secrets
- X: Kubernetes-first design
- XI: Cloud-agnostic architecture
- XII: No manual coding outside Spec-Kit
- XIII: Observability mandatory
- XIV: Every service event-driven

---

## Submission & Evaluation Rules

- Each phase MUST be independently demoable.
- The same repository will be submitted every Sunday.
- Phase-specific GitHub links may reference branches or tags.
- Demo videos MUST clearly show working functionality.

## Governance

### Final Authority

If any conflict arises:
1. This constitution takes priority.
2. Specs take priority over code.
3. Manual decisions are invalid without spec updates.

### Amendment Procedure

- Constitution amendments require explicit documentation.
- All changes MUST be versioned with semantic versioning.
- MAJOR: Backward incompatible governance/principle removals or redefinitions.
- MINOR: New principle/section added or materially expanded guidance.
- PATCH: Clarifications, wording, typo fixes, non-semantic refinements.

### Compliance Review

- All PRs/reviews MUST verify compliance with this constitution.
- Non-compliance MUST be flagged and resolved before merge.
- Phase V changes MUST additionally pass the Phase V Compliance Checklist (8 checks).

## Closing Statement

This hackathon evaluates:
- Your ability to think in systems
- Your mastery of Spec-Driven Development
- Your skill in using AI as a software architect

Clear specs produce clean systems.

**Version**: 1.1.0 | **Ratified**: 2025-01-07 | **Last Amended**: 2026-02-09
