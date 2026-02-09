---
id: 005
title: Phase V Constitution Update
stage: plan
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 003-phase-v-cloud-deployment
branch: 003-phase-v-cloud-deployment
user: developer
command: /sp.cerity
labels: ["constitution", "principles", "governance", "dapr", "kafka", "observability"]
links:
  spec: specs/003-phase-v-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none (principles document, no code)
---

## Prompt

/sp.cerity

Create or update the project constitution for Phase V.

Define NON-NEGOTIABLE rules:

- No direct Kafka client usage in app code
- All async communication via Dapr
- No secrets hard-coded
- Kubernetes-first design
- Cloud-agnostic architecture
- No manual coding outside Spec-Kit workflow
- Observability is mandatory
- Every service must be event-driven

This document defines PRINCIPLES, not features.
No code allowed.

## Response snapshot

Updated constitution from version 1.0.1 → 1.1.0 (MINOR). Added 8 non-negotiable Phase V principles (VII–XIV), a compliance checklist, and violation examples. Expanded the Phase V Phase Constitution section to reference all 8 principles.

New principles added:
- VII: No Direct Kafka Client Usage in Application Code
- VIII: All Asynchronous Communication Via Dapr
- IX: No Secrets Hard-Coded
- X: Kubernetes-First Design
- XI: Cloud-Agnostic Architecture
- XII: No Manual Coding Outside Spec-Kit Workflow
- XIII: Observability Is Mandatory
- XIV: Every Service Must Be Event-Driven

Each principle includes: the rule, rationale ("Why"), a violation example, the correct pattern, and spec basis (traced to FR numbers).

Added 8-point compliance checklist that every PR/code review must verify.

## Outcome

- ✅ Impact: Constitution v1.1.0 with 8 non-negotiable Phase V principles governing all implementation
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (updated)
- 🔁 Next prompts: Begin implementation with T-001 (Kafka setup) — all code must now comply with these principles
- 🧠 Reflection: Principles are enforceable because each includes a concrete violation example and the correct pattern — makes code review objective, not subjective

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Manual review — PASS (all 8 requested rules present, all traced to spec)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
