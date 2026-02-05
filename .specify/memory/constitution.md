<!--
  SYNC IMPACT REPORT
  ==================
  Version change: 1.0.0 → 1.0.1 (PATCH - Phase III clarification)

  Modified principles:
  - Phase III AI Behavior Rules: Changed "MCP tools" to "REST API endpoints"
  - Updated MCP Tools list to REST API Endpoints with specific endpoint paths

  Rationale:
  - Aligns constitution with actual implementation approach in spec.md and plan.md
  - Clarifies that AI must use existing Phase II REST endpoints, not MCP tools
  - Maintains core principle: AI must NOT directly access database

  Added sections: N/A

  Removed sections: N/A

  Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (no impact)
  - .specify/templates/spec-template.md ✅ (no impact)
  - .specify/templates/tasks-template.md ✅ (no impact)

  Follow-up TODOs: None
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
  - `/backend` → backend logic
  - `/frontend` → UI
  - `/infra`, `/docker`, `/k8s` → infrastructure
- Naming conventions MUST be consistent and meaningful.

### VI. Professional Quality Bar

- Code MUST be readable, maintainable, and production-grade.
- Unnecessary abstractions and over-engineering are prohibited.
- Best practices for each technology stack MUST be followed.

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

**Scope**: Deploy the system to a cloud Kubernetes provider.

**Cloud Providers** (Any One): Oracle Cloud (Recommended), Azure AKS, Google GKE

**Event-Driven Architecture**:
- Kafka MUST be used for: Task reminders, Recurring tasks, Activity/audit logs, Real-time synchronization.

**Reliability Rules**:
- System MUST tolerate restarts.
- Events MUST be durable and replayable.

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

## Closing Statement

This hackathon evaluates:
- Your ability to think in systems
- Your mastery of Spec-Driven Development
- Your skill in using AI as a software architect

Clear specs produce clean systems.

**Version**: 1.0.1 | **Ratified**: 2025-01-07 | **Last Amended**: 2026-02-01
