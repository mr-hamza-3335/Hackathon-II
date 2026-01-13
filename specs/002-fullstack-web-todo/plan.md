# Implementation Plan: Phase II Full-Stack Web Todo Application

**Branch**: `002-fullstack-web-todo` | **Date**: 2026-01-08 | **Updated**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-web-todo/spec.md`

## Summary

Transform the Phase I console Todo application into a multi-user full-stack web application. Users will register, authenticate via JWT (Better Auth), and manage personal task lists through a Next.js frontend. All task data persists in PostgreSQL (Neon Serverless). The Phase I console application MUST remain functional and unchanged.

**Technical Approach**: Add parallel `api/` (FastAPI) and `frontend/` (Next.js) directories alongside the protected `backend/` directory. Reuse domain concepts from Phase I while implementing new persistence and authentication layers.

## Technical Context

**Language/Version**: Python 3.13+ (API), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy, Better Auth, Next.js 14 (App Router), React 18
**Storage**: PostgreSQL (Neon Serverless)
**Testing**: pytest (API), Jest + React Testing Library (Frontend)
**Target Platform**: Web (modern browsers with JavaScript enabled)
**Project Type**: Web application (separate frontend/backend/api)
**Performance Goals**: 100 concurrent users, <2s task operations (SC-003, SC-007)
**Constraints**: <5s login-to-dashboard (SC-002), <1s validation feedback (SC-006)
**Scale/Scope**: Multi-user system, 7 user stories, 39 functional requirements, 9 non-functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase II Constitutional Requirements (from constitution.md)

| Gate | Requirement | Status | Notes |
|------|-------------|--------|-------|
| Architecture Stack | Frontend: Next.js (App Router), Backend: FastAPI, DB: PostgreSQL (Neon), Auth: Better Auth with JWT | ✅ PASS | Matches spec exactly |
| Security: API Authentication | All API endpoints MUST require authentication | ✅ PASS | Planned per FR-006 |
| Security: JWT Verification | JWT tokens MUST be verified on every request | ✅ PASS | Planned per FR-006 |
| Security: User Isolation | Users may ONLY access their own tasks | ✅ PASS | Planned per FR-008 |
| Data: User Association | Tasks MUST be associated with a user ID | ✅ PASS | Planned per FR-018 |
| Data: Query Filtering | All queries MUST be filtered by authenticated user | ✅ PASS | Planned per FR-008, FR-011 |

### Core Principles Compliance

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | ✅ PASS | All requirements from spec.md, no manual coding |
| II. Single Repository | ✅ PASS | Extending existing repo, new directories only |
| III. Evolution Over Rewrite | ✅ PASS | Phase I `backend/` directory untouched |
| IV. Single Source of Truth | ✅ PASS | Spec at `/specs/002-fullstack-web-todo/spec.md` |
| V. Clean Architecture | ✅ PASS | Separate `api/`, `frontend/`, `infra/` directories |
| VI. Professional Quality Bar | ✅ PASS | Production-grade patterns planned |

### Non-Functional Requirements Gate

| NFR | Requirement | Status |
|-----|-------------|--------|
| NFR-001 | Secure password hashing (bcrypt cost factor 12) | ✅ Will use bcrypt |
| NFR-002 | Token-based authentication (JWT HS256) | ✅ JWT via Better Auth |
| NFR-003 | Input sanitization | ✅ Pydantic + server validation |
| NFR-004 | Frontend/backend separation | ✅ Separate directories |
| NFR-005 | Responsive UI (1024px+/320px+) | ✅ Tailwind CSS responsive |
| NFR-006 | Phase I functional | ✅ `backend/` unchanged |
| NFR-007 | HTTP-only cookies (Secure, SameSite=Lax) | ✅ Cookie-based token storage |
| NFR-008 | Parameterized queries (ORM) | ✅ SQLAlchemy ORM |
| NFR-009 | XSS escaping for user content | ✅ React default escaping + sanitization |

**Gate Status: ✅ ALL GATES PASS - Proceed to Phase 0 Research**

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-todo/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-auth.yaml    # Authentication endpoints
│   └── api-tasks.yaml   # Task management endpoints
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/                           # [PROTECTED - Phase I console app]
├── src/
│   ├── models/
│   │   ├── task.py               # Phase I Task entity
│   │   └── exceptions.py         # Phase I exceptions
│   ├── services/
│   │   └── task_service.py       # Phase I in-memory service
│   └── cli/
│       ├── commands.py           # Phase I CLI
│       └── display.py            # Phase I display
└── tests/

api/                               # [NEW - Phase II FastAPI]
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── config.py                 # Environment configuration
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py               # Base model with common fields
│   │   ├── user.py               # User entity
│   │   └── task.py               # Task entity (extends Phase I concept)
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py               # Auth DTOs
│   │   ├── task.py               # Task DTOs
│   │   └── common.py             # Error response schemas
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py       # Authentication logic
│   │   └── task_service.py       # Task CRUD with user filtering
│   ├── routes/                   # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py               # /api/auth/* endpoints
│   │   └── tasks.py              # /api/tasks/* endpoints
│   ├── middleware/               # Cross-cutting concerns
│   │   ├── __init__.py
│   │   └── auth.py               # JWT verification middleware
│   └── db/                       # Database layer
│       ├── __init__.py
│       ├── connection.py         # Neon PostgreSQL connection
│       └── migrations/           # Alembic migrations
└── tests/
    ├── conftest.py               # Pytest fixtures
    ├── unit/
    │   ├── test_auth_service.py
    │   └── test_task_service.py
    └── integration/
        ├── test_auth_routes.py
        └── test_task_routes.py

frontend/                          # [NEW - Phase II Next.js]
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Landing/redirect
│   │   ├── (auth)/               # Auth route group
│   │   │   ├── login/
│   │   │   │   └── page.tsx      # Login page
│   │   │   └── register/
│   │   │       └── page.tsx      # Registration page
│   │   └── (protected)/          # Protected route group
│   │       └── dashboard/
│   │           └── page.tsx      # Task dashboard
│   ├── components/               # React components
│   │   ├── ui/                   # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Card.tsx
│   │   ├── auth/                 # Auth-specific components
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   └── tasks/                # Task-specific components
│   │       ├── TaskList.tsx
│   │       ├── TaskItem.tsx
│   │       ├── TaskForm.tsx
│   │       └── EmptyState.tsx
│   ├── lib/                      # Utilities and services
│   │   ├── api.ts                # API client wrapper
│   │   ├── auth.ts               # Auth utilities
│   │   └── validation.ts         # Client-side validation
│   └── types/                    # TypeScript type definitions
│       ├── auth.ts
│       └── task.ts
├── public/                       # Static assets
└── tests/
    ├── components/
    └── e2e/

infra/                             # [NEW - Phase II Infrastructure]
├── docker/
│   ├── api.Dockerfile
│   └── frontend.Dockerfile
└── docker-compose.yml            # Local development stack
```

**Structure Decision**: Web application structure with separate `api/` (FastAPI), `frontend/` (Next.js), and `infra/` (Docker) directories. Phase I `backend/` remains completely untouched to maintain backward compatibility per NFR-006.

## Complexity Tracking

> No constitution violations requiring justification.

| Area | Decision | Rationale |
|------|----------|-----------|
| Separate api/ directory | New directory instead of extending backend/ | NFR-006 requires Phase I unchanged |
| Layered FastAPI structure | models/schemas/services/routes separation | Clean Architecture principle, maintainability |
| Better Auth integration | Using Better Auth for JWT | Constitution mandates Better Auth |

---

## Phase 0: Research & Analysis

*See [research.md](./research.md) for complete findings.*

---

## Phase 1: Design & Contracts

*See [data-model.md](./data-model.md) for entity definitions.*
*See [contracts/](./contracts/) for API specifications.*
*See [quickstart.md](./quickstart.md) for setup guide.*

---

## Implementation Phases Overview

### Backend Implementation Order

1. **Database Layer** (Foundation)
   - Set up Neon PostgreSQL connection
   - Create SQLAlchemy models (User, Task)
   - Set up Alembic migrations

2. **Authentication Layer** (Security First)
   - Integrate Better Auth
   - Implement JWT token generation/validation
   - Create auth middleware

3. **Task API Layer** (Core Features)
   - Task CRUD endpoints with user filtering
   - Input validation with Pydantic
   - Error response formatting

### Frontend Implementation Order

1. **Project Setup** (Foundation)
   - Next.js App Router configuration
   - Tailwind CSS setup
   - API client setup

2. **Authentication UI** (Entry Point)
   - Login page
   - Registration page
   - Auth state management

3. **Task Dashboard** (Core Features)
   - Task list display
   - Add/edit/delete functionality
   - Complete/incomplete toggle

### Integration & Testing

1. **API Testing**
   - Unit tests for services
   - Integration tests for routes

2. **Frontend Testing**
   - Component tests
   - E2E tests (critical paths)

3. **Security Verification**
   - Cross-user access prevention
   - Token expiration handling

---

## Constitution Check: Post-Design Re-evaluation

*Re-evaluated after Phase 1 design completion.*

### Phase II Constitutional Requirements

| Gate | Requirement | Status | Design Evidence |
|------|-------------|--------|-----------------|
| Architecture Stack | Next.js + FastAPI + PostgreSQL + Better Auth | ✅ PASS | data-model.md, quickstart.md confirm stack |
| Security: API Auth | All endpoints require authentication | ✅ PASS | api-auth.yaml, api-tasks.yaml specify security |
| Security: JWT Verification | JWT verified on every request | ✅ PASS | Middleware design in research.md Section 3 |
| Security: User Isolation | Users access only their tasks | ✅ PASS | All task queries include user_id filter (data-model.md) |
| Data: User Association | Tasks linked to user_id | ✅ PASS | FK constraint in data-model.md |
| Data: Query Filtering | All queries filtered by user | ✅ PASS | Query patterns in data-model.md |

### Design Artifacts Verification

| Artifact | Status | Content Verified |
|----------|--------|------------------|
| research.md | ✅ Complete | 10 research areas covered |
| data-model.md | ✅ Complete | 2 entities, schemas, migrations defined |
| contracts/api-auth.yaml | ✅ Complete | 4 auth endpoints specified |
| contracts/api-tasks.yaml | ✅ Complete | 7 task endpoints specified |
| quickstart.md | ✅ Complete | Setup, dependencies, troubleshooting |

### Security Design Verification

| Security Concern | Design Solution | Reference |
|------------------|-----------------|-----------|
| Password storage | bcrypt hashing (cost factor 12) | spec.md NFR-001 |
| Token theft (XSS) | HTTP-only cookies | spec.md NFR-007 |
| Token expiration | 24-hour JWT lifetime | spec.md FR-028 |
| CSRF | SameSite=Lax cookie attribute | spec.md NFR-007 |
| SQL injection | SQLAlchemy ORM (parameterized) | spec.md NFR-008 |
| XSS prevention | Escape user-generated content | spec.md NFR-009 |
| Cross-user access | user_id filter on ALL queries | data-model.md Query Patterns |
| ID enumeration | UUIDs for all IDs | data-model.md Entity definitions |
| Rate limiting | 10/min auth, 100/min tasks | spec.md FR-036 to FR-039 |
| CORS | Frontend origin only | spec.md FR-034, FR-035 |
| API versioning | /api/v1/ prefix | spec.md FR-032, FR-033 |

### Phase I Protection Verification

| Check | Status | Evidence |
|-------|--------|----------|
| backend/ directory unchanged | ✅ CONFIRMED | New api/ directory created instead |
| Phase I can run independently | ✅ CONFIRMED | No dependencies added to Phase I |
| No shared code modifications | ✅ CONFIRMED | api/ has its own models/services |

**Post-Design Gate Status: ✅ ALL GATES PASS - Ready for /sp.tasks**

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Better Auth integration complexity | Medium | Medium | Start with basic JWT, extend later |
| Neon connection issues | Low | High | Connection pooling, retry logic |
| Cookie handling across domains | Medium | Medium | Proper CORS and SameSite config |
| Phase I regression | Low | High | No modifications to backend/ |

---

## Follow-up Items

1. Run `/sp.tasks` to generate implementation tasks from this plan
2. Create Neon PostgreSQL project for development
3. Verify Phase I console app runs successfully before starting Phase II
4. Review API contracts with stakeholders before implementation
