---
id: 001
title: Hackathon II Constitution Init
stage: constitution
date: 2025-01-07
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: Mak Tech
command: /sp.constitution
labels: ["constitution", "hackathon", "spec-driven-development", "init"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

# Spec-Kit Constitution

## Hackathon II – Evolution of Todo (AI / Spec-Driven Development)

---

## Purpose

This constitution defines the **rules, quality standards, and boundaries**
for the Hackathon II "Evolution of Todo" project.

All development MUST follow **Spec-Driven Development**.
Claude Code and the developer are both REQUIRED to follow this constitution
across all five phases of the hackathon.

Manual coding is strictly prohibited.

---

## Global Rules (Apply to ALL Phases)

### 1. Spec-Driven Development Only
- No code may be written or edited manually.
- Every feature MUST be defined in a markdown spec before implementation.
- If behavior is unclear or incorrect, the spec MUST be updated first.

### 2. Single Repository Rule
- The entire project MUST live in a single GitHub repository.
- Separate repositories per phase are NOT allowed.
- Project history and evolution must remain visible.

### 3. Evolution Over Rewrite
- Each phase must extend the previous phase.
- Existing functionality must not be rewritten or discarded unless explicitly stated in the spec.
- Backward compatibility must be preserved whenever possible.

### 4. Single Source of Truth
- All requirements live exclusively in `/specs/**`.
- README files, comments, or verbal instructions are NOT authoritative.
- Code behavior must always match the specs.

### 5. Clean Architecture
- Clear separation of concerns is required:
  - `/specs` → requirements
  - `/backend` → backend logic
  - `/frontend` → UI
  - `/infra`, `/docker`, `/k8s` → infrastructure
- Naming conventions must be consistent and meaningful.

### 6. Professional Quality Bar
- Code must be readable, maintainable, and production-grade.
- Avoid unnecessary abstractions and over-engineering.
- Follow best practices for each technology stack.

---

## Phase I Constitution – Console Todo Application

### Scope
- Command-line Todo application written in Python.
- Data stored ONLY in memory (no database).

### Functional Rules
- The application MUST support:
  - Add task
  - Update task
  - Delete task
  - List tasks
  - Mark task complete/incomplete

### Technical Rules
- Python 3.13+
- Clean project structure
- No persistence between runs

### Restrictions
- No external databases
- No web UI
- No authentication

---

## Phase II Constitution – Full-Stack Web Application

### Scope
- Transform the console app into a multi-user web application.

### Architecture
- Frontend: Next.js (App Router)
- Backend: FastAPI (Python)
- Database: PostgreSQL (Neon Serverless)
- Authentication: Better Auth with JWT

### Security Rules
- All API endpoints MUST require authentication.
- JWT tokens MUST be verified on every request.
- Users may ONLY access their own tasks.

### Data Rules
- Tasks must be associated with a user ID.
- All queries must be filtered by authenticated user.

---

## Phase III Constitution – AI-Powered Todo Chatbot

### Scope
- Introduce a conversational AI interface for managing todos.

### AI Behavior Rules
- The chatbot MUST:
  - Interpret natural language commands
  - Call MCP tools to manage tasks
  - Never directly manipulate the database

### MCP Tools
- add_task
- list_tasks
- update_task
- delete_task
- complete_task

### Stateless Design
- Each request must be handled independently.
- No server-side conversation memory is allowed.

---

## Phase IV Constitution – Local Kubernetes Deployment

### Scope
- Deploy the application locally using Kubernetes.

### Infrastructure Rules
- All services must be containerized using Docker.
- Kubernetes deployment must use:
  - Minikube
  - Helm charts

### AIOps
- Use kubectl-ai and kagent where applicable.
- Deployment must be reproducible.

---

## Phase V Constitution – Advanced Cloud Deployment

### Scope
- Deploy the system to a cloud Kubernetes provider.

### Cloud Providers (Any One)
- Oracle Cloud (Recommended)
- Azure AKS
- Google GKE

### Event-Driven Architecture
- Kafka MUST be used for:
  - Task reminders
  - Recurring tasks
  - Activity/audit logs
  - Real-time synchronization

### Reliability Rules
- System must tolerate restarts.
- Events must be durable and replayable.

---

## Submission & Evaluation Rules

- Each phase MUST be independently demoable.
- The same repository will be submitted every Sunday.
- Phase-specific GitHub links may reference branches or tags.
- Demo videos must clearly show working functionality.

---

## Final Authority

If any conflict arises:
1. This constitution takes priority.
2. Specs take priority over code.
3. Manual decisions are invalid without spec updates.

---

## Closing Statement

This hackathon evaluates:
- Your ability to think in systems
- Your mastery of Spec-Driven Development
- Your skill in using AI as a software architect

Clear specs produce clean systems.

## Response snapshot

Created project constitution v1.0.0 for Hackathon II "Evolution of Todo". The constitution establishes:
- 6 Core Principles (Spec-Driven Development, Single Repository, Evolution Over Rewrite, Single Source of Truth, Clean Architecture, Professional Quality)
- 5 Phase-specific constitutions (Console App → Full-Stack → AI Chatbot → Local K8s → Cloud)
- Governance rules with semantic versioning
- Final authority hierarchy (Constitution > Specs > Code)

## Outcome

- Impact: Initial constitution ratification establishing all project rules and quality standards
- Tests: N/A (documentation artifact)
- Files: .specify/memory/constitution.md created
- Next prompts: /sp.specify for Phase I Console Todo Application
- Reflection: Successfully transformed user's raw constitution input into structured, version-controlled project governance document

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - all placeholders filled, version correct, dates ISO format
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
