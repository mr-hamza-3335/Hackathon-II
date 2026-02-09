---
id: 001
title: Specify Backend Event Publishing
stage: spec
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 004-backend-event-publishing
branch: 004-backend-event-publishing
user: user
command: /sp.specify
labels: ["event-publishing", "dapr", "cloudevents", "kafka", "phase-v"]
links:
  spec: specs/004-backend-event-publishing/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-backend-event-publishing/spec.md
  - specs/004-backend-event-publishing/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

We have successfully completed **Phase V – Stage 3 (Dapr Components)**. All Helm templates for Kafka, Dapr state store, secret store, and subscriptions are implemented and verified. Now proceed with **Phase V – Stage 4: Backend Event Publishing** using the **Spec-Driven Development workflow (Specify → Plan → Tasks → Implement)**.

Create speckit.specify for Backend Event Publishing covering:
- Publish events for all task lifecycle actions: task.created, task.updated, task.completed, task.uncompleted, task.deleted
- Publish reminder events when due dates are set or updated
- Publish real-time sync events for websocket broadcasting
- Event types: task-events, reminders, task-updates
- Non-functional: async & non-blocking, failure to publish must NOT fail main API request, events must be traceable and auditable, compatible with Kafka via Dapr Pub/Sub abstraction
- Acceptance criteria: Events follow CloudEvents 1.0, events visible on Kafka topics via Dapr, existing Phase IV APIs continue to work unchanged

## Response snapshot

Created feature specification for Backend Event Publishing (Phase V Stage 4) with:
- 3 user stories: Task Lifecycle Events (P1), Real-Time Sync Events (P2), Reminder Events (P3)
- 15 functional requirements covering all event types, CloudEvents compliance, non-blocking publishing, and backward compatibility
- 3 key entities: TaskEvent, SyncEvent, ReminderEvent
- 6 measurable success criteria
- Quality checklist created and all items passed validation
- Branch created: 004-backend-event-publishing
- No [NEEDS CLARIFICATION] markers — all requirements are unambiguous

## Outcome

- ✅ Impact: Feature specification complete, ready for /sp.plan
- 🧪 Tests: N/A (specification phase)
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.plan to generate architectural plan
- 🧠 Reflection: Spec covers all 5 task lifecycle events + sync + reminder topics. Reminder events marked future-ready since Task model lacks due_date field.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist PASS (all items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
