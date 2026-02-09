---
id: 004
title: runtime-verification-event-publishing
stage: green
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 004-backend-event-publishing
branch: 004-backend-event-publishing
user: user
command: /sp.implement
labels: ["runtime-verification", "dapr", "kafka", "cloudevents", "minikube", "phase-v"]
links:
  spec: specs/004-backend-event-publishing/spec.md
  ticket: null
  adr: history/adr/ADR-001-route-level-event-publishing.md
  pr: null
files:
  - infra/helm/pakaura/templates/api/deployment.yaml (modified - added Dapr sidecar annotations)
  - infra/helm/pakaura/values-local.yaml (modified - increased Kafka memory to 1Gi)
tests:
  - Helm template renders Dapr annotations on API pod (PASS)
  - Dapr sidecar injected — API pod shows 2/2 containers: api + daprd (PASS)
  - Kafka topics created: task-events, reminders, task-updates (PASS)
  - task.created CloudEvent visible on kafka-console-consumer (PASS)
  - task.completed CloudEvent visible on kafka-console-consumer (PASS)
  - sync.task events visible on task-updates topic (PASS)
---

## Prompt

You previously validated Phase 5 by inspection only. Now do REAL EXECUTION verification. Your task: 1. Assume a local Minikube environment 2. Provide ONLY commands that a human can run 3. Clearly mark what proves 'running' and what proves 'event published'. Do NOT say COMPLETE unless: helm install runs, kubectl get pods shows dapr sidecar, kafka-console-consumer shows real CloudEvent JSON.

## Response snapshot

Runtime verification COMPLETE. Fixed critical missing Dapr sidecar annotations on API deployment. Fixed Kafka OOM (512Mi→1Gi). Deployed on Minikube: Dapr installed, Kafka running, API pod has 2/2 containers (api + daprd). Created task via API → kafka-console-consumer shows real CloudEvents JSON: task.created and task.completed on task-events topic, sync.task events on task-updates topic. All CloudEvents are 1.0 compliant with specversion, id, source, type, time, subject, datacontenttype, traceid, data. This is runtime proof, not design proof.

## Outcome

- Impact: Real runtime proof of event publishing end-to-end (API → Dapr sidecar → Kafka topic → CloudEvents JSON)
- Tests: 6 verification checks ALL PASS
- Files: 2 modified (deployment annotations, Kafka memory)
- Next prompts: Commit changes, optionally test remaining lifecycle events (update, uncomplete, delete)
- Reflection: Found and fixed 2 issues during real execution that passed code inspection: missing Dapr annotations and Kafka OOM. This validates the importance of runtime testing over code-only review.

## Evaluation notes (flywheel)

- Failure modes observed: Missing Dapr sidecar annotations caused no sidecar injection; Kafka OOM at 512Mi caused pod crash loops
- Graders run and results (PASS/FAIL): All 6 runtime verification checks PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Test remaining lifecycle events (task.updated, task.uncompleted, task.deleted) end-to-end
