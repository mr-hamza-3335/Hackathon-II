# Tasks: Phase II Full-Stack Web Todo Application

**Input**: Design documents from `/specs/002-fullstack-web-todo/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Created**: 2026-01-09
**Status**: Implementation Complete
**Completed**: 2026-01-09

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **API**: `api/src/` (FastAPI backend)
- **Frontend**: `frontend/src/` (Next.js)
- **Infrastructure**: `infra/` (Docker)

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure and dependencies

- [x] T001 Create api/ directory structure per plan.md: api/src/{models,schemas,services,routes,middleware,db}/
- [x] T002 Create frontend/ directory structure per plan.md: frontend/src/{app,components,lib,types}/
- [x] T003 Create infra/docker/ directory for Docker configuration
- [x] T004 [P] Initialize Python project with pyproject.toml in api/ with FastAPI, Pydantic, SQLAlchemy, bcrypt, python-jose dependencies
- [x] T005 [P] Initialize Next.js 14 project with TypeScript and Tailwind CSS in frontend/
- [x] T006 [P] Create .env.example files in api/ and frontend/ per quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [x] T007 Create database connection module in api/src/db/connection.py with async SQLAlchemy engine for Neon PostgreSQL
- [x] T008 Create base model with TimestampMixin in api/src/models/base.py per data-model.md
- [x] T009 [P] Create User ORM model in api/src/models/user.py per data-model.md
- [x] T010 [P] Create Task ORM model in api/src/models/task.py per data-model.md
- [x] T011 Create models/__init__.py exporting Base, User, Task
- [x] T012 Setup Alembic migrations framework in api/src/db/migrations/
- [x] T013 Create initial migration 001_initial_schema.py with users and tasks tables per data-model.md

### Configuration & Environment

- [x] T014 Create configuration module in api/src/config.py for environment variables (DATABASE_URL, JWT_SECRET, FRONTEND_URL, etc.)
- [x] T015 [P] Create common error response schemas in api/src/schemas/common.py per FR-026 format

### Security Middleware (FR-032 to FR-039)

- [x] T016 Create JWT verification middleware in api/src/middleware/auth.py with 24-hour expiration check (FR-028, FR-029)
- [x] T017 Create rate limiting middleware in api/src/middleware/rate_limit.py with 10 req/min auth (FR-036), 100 req/min tasks (FR-037)
- [x] T018 Create CORS configuration in api/src/main.py allowing only FRONTEND_URL origin (FR-034, FR-035)

### FastAPI Application Entry

- [x] T019 Create FastAPI application in api/src/main.py with CORS middleware, rate limiting, and /api/v1/ router prefix (FR-032)
- [x] T020 Create health check endpoint GET /api/v1/health in api/src/routes/__init__.py

### Frontend Foundation

- [x] T021 Create root layout with providers in frontend/src/app/layout.tsx
- [x] T022 [P] Create TypeScript types for User in frontend/src/types/auth.ts per data-model.md
- [x] T023 [P] Create TypeScript types for Task in frontend/src/types/task.ts per data-model.md
- [x] T024 Create API client wrapper with credentials:include in frontend/src/lib/api.ts per research.md Section 6
- [x] T025 Create client-side validation utilities in frontend/src/lib/validation.ts for email and password rules
- [x] T026 [P] Create reusable Button component in frontend/src/components/ui/Button.tsx
- [x] T027 [P] Create reusable Input component in frontend/src/components/ui/Input.tsx
- [x] T028 [P] Create reusable Card component in frontend/src/components/ui/Card.tsx

### Docker Infrastructure

- [x] T029 [P] Create api.Dockerfile in infra/docker/ for FastAPI service
- [x] T030 [P] Create frontend.Dockerfile in infra/docker/ for Next.js service
- [x] T031 Create docker-compose.yml in infra/ with api, frontend, and local postgres services per research.md Section 10

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Registration (Priority: P1)

**Goal**: New visitors can create accounts and start using the Todo application

**Independent Test**: Register with valid email/password, verify account created and redirected to dashboard

**Spec Reference**: User Story 1, FR-001, FR-002, FR-003, FR-005, NFR-001, NFR-002

### Backend Implementation

- [x] T032 [P] [US1] Create auth request/response schemas in api/src/schemas/auth.py per data-model.md (UserRegisterRequest, UserLoginRequest, UserResponse)
- [x] T033 [US1] Create auth service in api/src/services/auth_service.py with register() method: email uniqueness check, bcrypt hashing (cost 12), JWT generation (HS256, 24h expiry)
- [x] T034 [US1] Create POST /api/v1/auth/register endpoint in api/src/routes/auth.py per api-auth.yaml contract
- [x] T035 [US1] Implement HTTP-only cookie setting in register endpoint with Secure, SameSite=Lax per NFR-007

### Frontend Implementation

- [x] T036 [P] [US1] Create register page route structure in frontend/src/app/(auth)/register/page.tsx
- [x] T037 [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx with email/password fields, client-side validation (8 char min)
- [x] T038 [US1] Implement form submission calling POST /api/v1/auth/register with error handling for 400/409 responses
- [x] T039 [US1] Implement success redirect to /dashboard after registration

**Checkpoint**: User Story 1 complete - visitors can register accounts

---

## Phase 4: User Story 2 - User Login (Priority: P1)

**Goal**: Registered users can log in to access their task list

**Independent Test**: Log in with valid credentials, verify redirected to dashboard; log out, verify session terminated

**Spec Reference**: User Story 2, FR-004, FR-005, FR-006, FR-007, FR-028, FR-029, FR-031

### Backend Implementation

- [x] T040 [US2] Extend auth service in api/src/services/auth_service.py with login() method: email lookup (case-insensitive), password verification, JWT generation
- [x] T041 [US2] Create POST /api/v1/auth/login endpoint in api/src/routes/auth.py per api-auth.yaml with generic error message (no field reveal)
- [x] T042 [US2] Create POST /api/v1/auth/logout endpoint in api/src/routes/auth.py clearing HTTP-only cookie (FR-031)
- [x] T043 [US2] Create GET /api/v1/auth/me endpoint in api/src/routes/auth.py returning current user info

### Frontend Implementation

- [x] T044 [P] [US2] Create login page route structure in frontend/src/app/(auth)/login/page.tsx
- [x] T045 [US2] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx with email/password fields
- [x] T046 [US2] Implement login form submission calling POST /api/v1/auth/login with error handling
- [x] T047 [US2] Implement success redirect to /dashboard after login
- [x] T048 [US2] Create auth utilities in frontend/src/lib/auth.ts for logout function and auth state check

### Auth Protection

- [x] T049 [US2] Create Next.js middleware in frontend/src/middleware.ts to redirect unauthenticated users to /login (FR-024)
- [x] T050 [US2] Create protected route group layout in frontend/src/app/(protected)/layout.tsx with auth check

**Checkpoint**: User Story 2 complete - users can log in and log out

---

## Phase 5: User Story 3 - Add Task (Priority: P1)

**Goal**: Authenticated users can add new tasks to their personal task list

**Independent Test**: Log in, add task with valid title, verify task appears in list and persists after refresh

**Spec Reference**: User Story 3, FR-009, FR-010, FR-016, FR-017, FR-018

### Backend Implementation

- [x] T051 [P] [US3] Create task request/response schemas in api/src/schemas/task.py per data-model.md (TaskCreateRequest, TaskResponse, TaskListResponse)
- [x] T052 [US3] Create task service in api/src/services/task_service.py with create() method: validate title, associate user_id, persist to database
- [x] T053 [US3] Create POST /api/v1/tasks endpoint in api/src/routes/tasks.py per api-tasks.yaml contract with auth dependency

### Frontend Implementation

- [x] T054 [P] [US3] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx with title input and submit button
- [x] T055 [US3] Implement form submission calling POST /api/v1/tasks with title validation (1-500 chars, non-empty)
- [x] T056 [US3] Implement immediate feedback: add new task to UI list on success (FR-023)

**Checkpoint**: User Story 3 complete - users can add tasks

---

## Phase 6: User Story 4 - View Task List (Priority: P1)

**Goal**: Authenticated users can view all their tasks with status indicators

**Independent Test**: Log in with user who has tasks, verify all tasks visible; log in as different user, verify only their tasks shown

**Spec Reference**: User Story 4, FR-011, FR-008, FR-022

### Backend Implementation

- [x] T057 [US4] Extend task service in api/src/services/task_service.py with list() method: filter by user_id (FR-008), order by created_at desc
- [x] T058 [US4] Create GET /api/v1/tasks endpoint in api/src/routes/tasks.py per api-tasks.yaml with optional completed filter

### Frontend Implementation

- [x] T059 [P] [US4] Create dashboard page in frontend/src/app/(protected)/dashboard/page.tsx
- [x] T060 [P] [US4] Create TaskList component in frontend/src/components/tasks/TaskList.tsx with task rendering
- [x] T061 [P] [US4] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx displaying title and status
- [x] T062 [P] [US4] Create EmptyState component in frontend/src/components/tasks/EmptyState.tsx for no-tasks message
- [x] T063 [US4] Implement dashboard data fetching calling GET /api/v1/tasks on mount
- [x] T064 [US4] Implement visual distinction between complete/incomplete tasks using CSS styling (FR-022)

**Checkpoint**: User Story 4 complete - users can view their task list

---

## Phase 7: User Story 5 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Authenticated users can toggle task completion status

**Independent Test**: Add task, mark complete, verify visual change and status persists; toggle back to incomplete

**Spec Reference**: User Story 5, FR-012, FR-013, FR-017

### Backend Implementation

- [x] T065 [US5] Extend task service in api/src/services/task_service.py with toggle_complete() method with user_id verification
- [x] T066 [US5] Create POST /api/v1/tasks/{taskId}/complete endpoint in api/src/routes/tasks.py per api-tasks.yaml
- [x] T067 [US5] Create POST /api/v1/tasks/{taskId}/uncomplete endpoint in api/src/routes/tasks.py per api-tasks.yaml

### Frontend Implementation

- [x] T068 [US5] Add completion toggle handler to TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [x] T069 [US5] Implement immediate visual feedback on status toggle (FR-023)
- [x] T070 [US5] Implement API calls for complete/uncomplete with error handling

**Checkpoint**: User Story 5 complete - users can toggle task status

---

## Phase 8: User Story 6 - Update Task Title (Priority: P3)

**Goal**: Authenticated users can edit task titles

**Independent Test**: Create task, edit title, verify change persists after refresh

**Spec Reference**: User Story 6, FR-014, FR-016

### Backend Implementation

- [x] T071 [P] [US6] Create TaskUpdateRequest schema in api/src/schemas/task.py per data-model.md
- [x] T072 [US6] Extend task service in api/src/services/task_service.py with update() method: title validation, user_id verification
- [x] T073 [US6] Create PATCH /api/v1/tasks/{taskId} endpoint in api/src/routes/tasks.py per api-tasks.yaml

### Frontend Implementation

- [x] T074 [US6] Add edit mode to TaskItem component in frontend/src/components/tasks/TaskItem.tsx with inline editing
- [x] T075 [US6] Implement title validation on edit (1-500 chars) with error display
- [x] T076 [US6] Implement API call for task update with success feedback

**Checkpoint**: User Story 6 complete - users can edit task titles

---

## Phase 9: User Story 7 - Delete Task (Priority: P3)

**Goal**: Authenticated users can permanently remove tasks

**Independent Test**: Create task, delete it, verify removed from list and database

**Spec Reference**: User Story 7, FR-015

### Backend Implementation

- [x] T077 [US7] Extend task service in api/src/services/task_service.py with delete() method: user_id verification, permanent deletion
- [x] T078 [US7] Create DELETE /api/v1/tasks/{taskId} endpoint in api/src/routes/tasks.py per api-tasks.yaml

### Frontend Implementation

- [x] T079 [US7] Add delete button to TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [x] T080 [US7] Implement delete confirmation (optional) and API call
- [x] T081 [US7] Implement immediate removal from UI list on successful deletion

**Checkpoint**: User Story 7 complete - users can delete tasks

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, error handling, and validation improvements

### Error Handling & Partial Failures

- [x] T082 Create global exception handler in api/src/main.py for database errors (HTTP 500/503) per Partial Failure Scenarios
- [x] T083 [P] Add rate limit exceeded response (HTTP 429 with Retry-After header) in api/src/middleware/rate_limit.py (FR-038)
- [x] T084 [P] Create frontend error boundary component in frontend/src/components/ErrorBoundary.tsx

### Security Hardening

- [x] T085 Verify XSS escaping for user content in TaskItem component (NFR-009)
- [x] T086 Verify parameterized queries in all SQLAlchemy operations (NFR-008)
- [x] T087 Add authorization error (HTTP 403) for cross-user task access attempts in api/src/services/task_service.py (Edge Case)

### Responsive UI (NFR-005)

- [x] T088 [P] Add responsive styling to LoginForm for mobile (320px+) and desktop (1024px+)
- [x] T089 [P] Add responsive styling to RegisterForm for mobile and desktop
- [x] T090 [P] Add responsive styling to dashboard and TaskList for mobile and desktop

### API Endpoint Completion

- [x] T091 Create GET /api/v1/tasks/{taskId} endpoint in api/src/routes/tasks.py per api-tasks.yaml

### Landing Page

- [x] T092 Create landing page in frontend/src/app/page.tsx with redirect logic based on auth status

### Quickstart Validation

- [x] T093 Run quickstart.md validation: verify all environment variables documented
- [x] T094 Test Docker Compose stack: docker-compose up builds and runs successfully

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
┌───┴───┬───────┬───────┐
↓       ↓       ↓       ↓
US1     US2     US3     US4  (P1 stories - can run in parallel after Phase 2)
        ↓
     US5 (P2 - depends on US4 for task list UI)
        ↓
  ┌─────┴─────┐
  ↓           ↓
US6         US7  (P3 stories - can run in parallel)
  └─────┬─────┘
        ↓
Phase 10 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Registration) | Phase 2 | Foundational complete |
| US2 (Login) | Phase 2 | Foundational complete |
| US3 (Add Task) | Phase 2, US2 (auth) | Login working |
| US4 (View List) | Phase 2, US2 (auth) | Login working |
| US5 (Toggle Status) | US4 | Task list visible |
| US6 (Update Title) | US4 | Task list visible |
| US7 (Delete Task) | US4 | Task list visible |

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
- T009, T010: User and Task models
- T022, T023: TypeScript types
- T026, T027, T028: UI components
- T029, T030: Dockerfiles

**Within User Stories**:
- US1 and US2 can proceed in parallel once Phase 2 complete
- US3 and US4 can proceed in parallel once US2 login working
- US6 and US7 can proceed in parallel once US4 list visible

---

## Parallel Example: Phase 2 Foundational

```bash
# After T011 (models init), launch in parallel:
Task T022: "Create TypeScript types for User in frontend/src/types/auth.ts"
Task T023: "Create TypeScript types for Task in frontend/src/types/task.ts"
Task T026: "Create reusable Button component in frontend/src/components/ui/Button.tsx"
Task T027: "Create reusable Input component in frontend/src/components/ui/Input.tsx"
Task T028: "Create reusable Card component in frontend/src/components/ui/Card.tsx"
Task T029: "Create api.Dockerfile in infra/docker/"
Task T030: "Create frontend.Dockerfile in infra/docker/"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T031) - **CRITICAL GATE**
3. Complete Phase 3: User Story 1 - Registration (T032-T039)
4. Complete Phase 4: User Story 2 - Login (T040-T050)
5. Complete Phase 5: User Story 3 - Add Task (T051-T056)
6. Complete Phase 6: User Story 4 - View List (T057-T064)
7. **STOP and VALIDATE**: Full user flow works (register → login → add task → view list)

### Incremental Delivery

| Increment | User Stories | Deliverable |
|-----------|--------------|-------------|
| MVP | US1-US4 | Users can register, login, add tasks, view list |
| v1.1 | + US5 | Toggle task completion |
| v1.2 | + US6, US7 | Edit and delete tasks |
| v1.3 | + Polish | Error handling, responsive, security hardening |

---

## Summary

| Category | Count |
|----------|-------|
| Total Tasks | 94 |
| Phase 1 (Setup) | 6 |
| Phase 2 (Foundational) | 25 |
| User Story 1 (Registration) | 8 |
| User Story 2 (Login) | 11 |
| User Story 3 (Add Task) | 6 |
| User Story 4 (View List) | 8 |
| User Story 5 (Toggle Status) | 6 |
| User Story 6 (Update Title) | 6 |
| User Story 7 (Delete Task) | 5 |
| Phase 10 (Polish) | 13 |

**Parallel Opportunities**: 28 tasks marked [P]

**Scope Verification**:
- Rate limiting: T017, T083 (FR-036 to FR-039)
- CORS: T018 (FR-034, FR-035)
- API versioning: T019 (FR-032, FR-033)
- Auth/JWT: T016, T033-T035, T040-T043 (FR-028 to FR-031)
- No AI/chatbot tasks (Phase III scope)
- No Kubernetes tasks (Phase IV scope)
- No Kafka/Cloud tasks (Phase V scope)
