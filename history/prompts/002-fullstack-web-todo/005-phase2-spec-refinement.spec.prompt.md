---
id: 005
title: Phase II Spec Refinement from Checklist
stage: spec
date: 2026-01-08
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-todo
branch: 002-fullstack-web-todo
user: developer
command: /sp.specify
labels: ["spec-refinement", "checklist-driven", "security", "api-versioning", "rate-limiting"]
links:
  spec: specs/002-fullstack-web-todo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fullstack-web-todo/spec.md
  - specs/002-fullstack-web-todo/checklists/phase2-quality.md
tests:
  - N/A (spec refinement)
---

## Prompt

Refine and update the Phase II specifications based on the quality checklist findings.

Please explicitly define the following in the specs:

1. Authentication token expiration policy
   - Specify token lifetime and renewal behavior

2. Rate limiting requirements
   - Define scope (per user / per IP)
   - Define intent (basic abuse prevention)

3. CORS configuration
   - Allowed origins for frontend-backend communication

4. API versioning strategy
   - Define versioning approach for REST endpoints

5. Partial failure scenarios
   - Define behavior for database errors, auth failures, and validation errors

Update the specs only.
Do not write any code.
Do not expand scope beyond Phase II.

## Response snapshot

Updated spec.md with 12 new functional requirements and 3 new non-functional requirements addressing checklist gaps:

**Token & Session Management (FR-028 to FR-031):**
- FR-028: 24-hour JWT token expiration
- FR-029: Expired token rejection with login redirect
- FR-030: No token refresh for Phase II (explicit exclusion)
- FR-031: Immediate cookie clearing on logout

**API Versioning & Configuration (FR-032 to FR-035):**
- FR-032: URL path versioning with /api/v1/ prefix
- FR-033: No multiple API versions for Phase II
- FR-034: CORS configured for frontend origin only
- FR-035: Unauthorized origins rejected

**Rate Limiting (FR-036 to FR-039):**
- FR-036: 10 req/min per IP for auth endpoints
- FR-037: 100 req/min per user for task endpoints
- FR-038: HTTP 429 with Retry-After header
- FR-039: No blocking of legitimate usage

**Enhanced NFRs:**
- NFR-001: Added "bcrypt with cost factor 12"
- NFR-002: Added "JWT with HS256 algorithm"
- NFR-005: Added responsive breakpoints (1024px+/320px+)
- NFR-007: HTTP-only cookies with Secure, SameSite=Lax
- NFR-008: Parameterized queries (ORM)
- NFR-009: XSS escaping for user content

**New Section - Partial Failure Scenarios:**
- Database write/read failures (HTTP 500/503)
- Auth service failure (HTTP 503)
- Validation failure (HTTP 400)
- Rate limit exceeded (HTTP 429)
- Atomic failure handling

**Checklist Results:**
- Before: Multiple gaps identified
- After: 55/60 items passed (92%)
- 5 remaining gaps are acceptable for Phase II

## Outcome

- ✅ Impact: Spec completeness improved from ~75% to 92% of checklist items
- 🧪 Tests: N/A (spec updates only)
- 📁 Files: 2 files updated (spec.md, phase2-quality.md)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Checklist-driven refinement is effective for catching gaps. Security completeness now at 100%.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Checklist validation PASS (55/60, 5 acceptable gaps)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Auto-generate spec refinements from checklist gaps
