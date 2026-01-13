---
id: 003
title: Phase II Implementation Plan
stage: plan
date: 2026-01-08
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-todo
branch: 002-fullstack-web-todo
user: developer
command: /sp.plan
labels: ["planning", "architecture", "fastapi", "nextjs", "postgresql", "jwt"]
links:
  spec: specs/002-fullstack-web-todo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fullstack-web-todo/plan.md
  - specs/002-fullstack-web-todo/research.md
  - specs/002-fullstack-web-todo/data-model.md
  - specs/002-fullstack-web-todo/quickstart.md
  - specs/002-fullstack-web-todo/contracts/api-auth.yaml
  - specs/002-fullstack-web-todo/contracts/api-tasks.yaml
tests:
  - N/A (planning phase)
---

## Prompt

Create a detailed implementation plan for Phase II.

The plan must include:
- Backend architecture (FastAPI layers)
- Database schema and migrations
- Authentication flow with JWT
- Frontend structure using Next.js App Router
- API endpoints and data flow

Rules:
- Follow Spec-Kit Constitution
- Do not write any code
- Do not include AI or future phases

The plan should be incremental and safe.

## Response snapshot

Created comprehensive implementation plan for Phase II full-stack web todo application:

**Phase 0 (Research):**
- Researched FastAPI layered architecture (models/schemas/services/routes)
- Defined database schema for PostgreSQL (Neon Serverless)
- Designed JWT authentication flow with Better Auth and HTTP-only cookies
- Established error response format per FR-026
- Documented security mitigations (XSS, CSRF, SQL injection)

**Phase 1 (Design & Contracts):**
- Created data model with User and Task entities (UUIDs, timestamps, FK relationships)
- Defined SQLAlchemy ORM models and Pydantic schemas
- Generated OpenAPI contracts for auth (4 endpoints) and tasks (7 endpoints)
- Documented query patterns with user_id filtering for isolation
- Created quickstart guide with setup instructions

**Key Architecture Decisions:**
- Separate `api/` directory (does NOT modify protected `backend/`)
- Layered FastAPI structure for maintainability
- HTTP-only cookies for token storage (XSS protection)
- All task queries filtered by authenticated user_id

**Constitution Compliance:**
- All gates passed (pre and post-design)
- Phase I `backend/` directory remains untouched
- Clean Architecture principles followed

## Outcome

- ✅ Impact: Complete implementation plan ready for /sp.tasks
- 🧪 Tests: N/A (planning phase - no code written)
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, api-auth.yaml, api-tasks.yaml)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Plan is comprehensive and incremental. Key risk is Better Auth integration complexity.

## Evaluation notes (flywheel)

- Failure modes observed: None - all constitution gates passed
- Graders run and results (PASS/FAIL): Constitution Check PASS (pre and post-design)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding sequence diagrams for auth flow in future plans
