---
id: 003
title: Phase V Technical Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 003-phase-v-cloud-deployment
branch: 003-phase-v-cloud-deployment
user: developer
command: /sp.plan
labels: ["architecture", "kafka", "dapr", "kubernetes", "ci-cd", "microservices"]
links:
  spec: specs/003-phase-v-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-phase-v-cloud-deployment/plan.md
tests:
  - none (architecture/design only)
---

## Prompt

/sp.plan

Using the approved Phase V specification, create a **detailed technical plan**.

RULES:
- No code
- No tasks
- Architecture & design only

### Plan Must Include

#### System Architecture
- Kubernetes-based microservices
- Event-driven communication
- Dapr sidecars per service

#### Services
- Frontend (Next.js)
- Chat API (FastAPI + MCP)
- Notification service
- Recurring task service
- Audit service
- WebSocket service

#### Kafka Design
- Topics: task-events, reminders, task-updates
- Producers & consumers per service

#### Dapr Components
- pubsub.kafka
- state store
- secret store
- jobs/scheduler
- service invocation

#### Deployment Strategy
- Minikube (local)
- Cloud Kubernetes (AKS/GKE/OKE)
- Helm chart reuse from Phase IV

#### CI/CD
- GitHub Actions pipeline stages
- Build, test, deploy

Ensure every design decision maps back to the specification.

## Response snapshot

Created comprehensive technical plan at `specs/003-phase-v-cloud-deployment/plan.md` with 14 sections:

1. **System Architecture** — 6 services + Kafka + PostgreSQL + monitoring on Kubernetes with Dapr sidecars. ASCII diagram showing all services and communication layers.
2. **Services** — Detailed inventory of all 6 services (Frontend, Chat API, Notification, Recurring, Audit, WebSocket Gateway) with roles, Dapr building blocks, resource budgets, and spec references.
3. **Kafka Design** — 3 topics (task-events, reminders, task-updates), partitioned by user_id. Complete producer/consumer mapping per service. CloudEvents v1.0 payload schema. 4 event flow diagrams mapping to the 4 constitution-mandated Kafka use cases.
4. **Dapr Components** — pubsub-kafka, statestore-redis, secretstore-k8s, jobs-scheduler. Subscription mapping for all services. Service invocation routes.
5. **Database Schema Evolution** — Migration 003 with 5 new tables and task table extensions.
6. **API Contract Evolution** — Extended and new REST endpoints, WebSocket endpoint, internal Dapr endpoints.
7. **Project Structure** — Full directory layout showing EXTEND vs NEW annotations for all files.
8. **Deployment Strategy** — Local (Minikube) and Production (Oracle OKE) with Helm values layering and fallback to AKS/GKE.
9. **CI/CD** — 4-stage GitHub Actions pipeline (Test → Build → Deploy → Verify), secrets management, rollback via Helm.
10. **Monitoring** — Prometheus + Grafana + Loki + Promtail stack, structured JSON logging, 8 metrics, health probes, 4 Grafana dashboards.
11. **Key Design Decisions** — 8 decisions with rationale and rejected alternatives.
12. **Complexity Tracking** — All new complexity traced to spec requirements.
13. **Risk Analysis** — 6 risks with mitigations.
14. **Post-Design Constitution Re-Check** — All gates PASS.

## Outcome

- ✅ Impact: Complete architecture and design plan for Phase V cloud deployment
- 🧪 Tests: N/A (architecture only, no code)
- 📁 Files: specs/003-phase-v-cloud-deployment/plan.md (written)
- 🔁 Next prompts: /sp.tasks to break plan into implementable tasks
- 🧠 Reflection: Plan evolved from initial draft to comprehensive version covering all 6 user-requested sections with full spec traceability

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Manual review — PASS (all requested sections present, all decisions map to spec)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
