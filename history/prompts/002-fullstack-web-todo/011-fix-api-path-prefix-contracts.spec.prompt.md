---
id: 011
title: Fix API Path Prefix in Contracts
stage: spec
date: 2026-01-09
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-todo
branch: 002-fullstack-web-todo
user: developer
command: /sp.specify
labels: ["fix", "contracts", "api-versioning", "FR-032"]
links:
  spec: specs/002-fullstack-web-todo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fullstack-web-todo/contracts/api-auth.yaml
  - specs/002-fullstack-web-todo/contracts/api-tasks.yaml
tests:
  - (no tests - spec correction only)
---

## Prompt

Fix HIGH severity issues identified by cross-artifact analysis.

Action required:
- Update contracts/api-auth.yaml
- Update contracts/api-tasks.yaml

Ensure:
- All API paths use the /api/v1/ prefix
- Paths are consistent with FR-032 and FR-033
- No behavior changes beyond path prefix correction

This is a spec-only correction.
Do not write or modify any implementation code.
Do not expand scope.

## Response snapshot

**Issue Fixed**: HIGH severity inconsistency (I1, I2) from /sp.analyze report

**Changes Made**:
- `api-auth.yaml`: Updated 4 paths
  - `/api/auth/register` → `/api/v1/auth/register`
  - `/api/auth/login` → `/api/v1/auth/login`
  - `/api/auth/logout` → `/api/v1/auth/logout`
  - `/api/auth/me` → `/api/v1/auth/me`

- `api-tasks.yaml`: Updated 4 paths
  - `/api/tasks` → `/api/v1/tasks`
  - `/api/tasks/{taskId}` → `/api/v1/tasks/{taskId}`
  - `/api/tasks/{taskId}/complete` → `/api/v1/tasks/{taskId}/complete`
  - `/api/tasks/{taskId}/uncomplete` → `/api/v1/tasks/{taskId}/uncomplete`

**Verification**: Grep confirmed no `/api/auth` or `/api/tasks` paths remain without `v1` prefix.

**Consistency**: All 8 API paths now align with FR-032 (URL path versioning with `/api/v1/` prefix).

## Outcome

- ✅ Impact: HIGH severity issues resolved; contracts now consistent with spec FR-032/FR-033
- 🧪 Tests: N/A (spec correction only)
- 📁 Files: 2 modified (api-auth.yaml, api-tasks.yaml)
- 🔁 Next prompts: Ready for /sp.implement
- 🧠 Reflection: Simple path prefix correction; no scope expansion; artifacts now internally consistent

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Path consistency PASS
- Prompt variant (if applicable): Standard /sp.specify for spec correction
- Next experiment (smallest change to try): N/A - correction complete
