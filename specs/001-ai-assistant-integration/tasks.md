# Phase 3 Implementation Tasks: AI Assistant Integration

**Feature Branch**: `001-ai-assistant-integration`
**Created**: 2026-01-13
**Status**: Ready for Implementation
**Specification**: [spec.md](./spec.md)

---

## Task Overview

| Phase | Tasks | Description |
|-------|-------|-------------|
| Foundation | P3-T01 to P3-T03 | Contracts, schemas, and configuration |
| Backend | P3-T04 to P3-T07 | API endpoint, intent routing, security |
| Frontend | P3-T08 to P3-T11 | UI components, theming, animations |
| Quality | P3-T12 to P3-T14 | Error handling, testing, verification |
| Delivery | P3-T15 | Git tagging and submission |

---

## Execution Order & Dependencies

```
P3-T01 (Prompt Contract)
    ↓
P3-T02 (Intent Schema)
    ↓
P3-T03 (Environment Config)
    ↓
P3-T04 (Backend AI Endpoint) ←─── depends on T01, T02, T03
    ↓
P3-T05 (Intent Validation & Routing) ←─── depends on T04
    ↓
P3-T06 (Task API Integration) ←─── depends on T05
    ↓
P3-T07 (Security & Rate Limiting) ←─── depends on T06
    ↓
P3-T08 (Frontend Chat UI) ←─── depends on T04
    ↓
P3-T09 (Dark/Light Mode) ←─── depends on T08
    ↓
P3-T10 (Animations & UX Polish) ←─── depends on T09
    ↓
P3-T11 (Frontend Error Handling) ←─── depends on T10
    ↓
P3-T12 (Backend Error Handling) ←─── depends on T07
    ↓
P3-T13 (Unit & Integration Tests) ←─── depends on T11, T12
    ↓
P3-T14 (End-to-End Verification) ←─── depends on T13
    ↓
P3-T15 (Git Tagging & Submission) ←─── depends on T14
```

---

## Implementation Tasks

### P3-T01: AI Prompt Contract Creation

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T01 |
| **Order** | 1 |
| **Description** | Define the system prompt and user prompt templates that govern AI behavior. Create the prompt contract file with strict rules for task management scope, response format, and safety guardrails as specified in spec Section 7. |
| **Dependencies** | None (Foundation task) |
| **Spec References** | FR-305, FR-306, FR-307, AIR-001 to AIR-020 |
| **Acceptance Criteria** | <ul><li>[ ] System prompt file created at `api/src/ai/prompts.py`</li><li>[ ] System prompt includes role definition, strict rules, capabilities list</li><li>[ ] User prompt template includes placeholders for user_input and current_tasks</li><li>[ ] Response format JSON schema documented in prompt</li><li>[ ] Scope limitation rules (AIR-001 to AIR-005) embedded in prompt</li><li>[ ] Safety rules (AIR-016 to AIR-020) embedded in prompt</li><li>[ ] Prompt enforces task-only scope with explicit refusal for off-topic requests</li></ul> |

---

### P3-T02: Intent Schema Definition

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T02 |
| **Order** | 2 |
| **Description** | Define TypeScript/Python schemas for AI request/response structures. Create enum for intent types and Pydantic models for structured JSON responses. |
| **Dependencies** | P3-T01 |
| **Spec References** | FR-307, FR-319, FR-320, FR-321, FR-322 |
| **Acceptance Criteria** | <ul><li>[ ] Intent enum created: CREATE, LIST, COMPLETE, UNCOMPLETE, UPDATE, DELETE, CLARIFY, ERROR, INFO</li><li>[ ] Pydantic model for AIRequest with fields: message (str), conversation_id (optional)</li><li>[ ] Pydantic model for AIResponse with fields: intent, message, action, data</li><li>[ ] Action schema with type (api_call/none), endpoint, method, payload</li><li>[ ] TypeScript types created in `frontend/src/types/ai.ts` matching backend schemas</li><li>[ ] Validation tests pass for all schema models</li></ul> |

---

### P3-T03: Environment Configuration

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T03 |
| **Order** | 3 |
| **Description** | Configure AI model API credentials and settings. Add environment variables for AI service integration (API key, model name, timeout). |
| **Dependencies** | None |
| **Spec References** | Assumptions section, NFR-301 |
| **Acceptance Criteria** | <ul><li>[ ] Environment variables added: AI_API_KEY, AI_MODEL_NAME, AI_TIMEOUT_SECONDS</li><li>[ ] `.env.example` updated with placeholder values</li><li>[ ] Config class in `api/src/config.py` extended with AI settings</li><li>[ ] Default timeout set to 10 seconds per NFR-301</li><li>[ ] AI API key NOT committed to repository</li><li>[ ] Documentation added for required environment variables</li></ul> |

---

### P3-T04: Backend AI Endpoint

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T04 |
| **Order** | 4 |
| **Description** | Create FastAPI endpoint `/api/v1/ai/chat` that receives user messages, processes them through the AI model, and returns structured responses. |
| **Dependencies** | P3-T01, P3-T02, P3-T03 |
| **Spec References** | FR-301, FR-309, FR-310, FR-311, Section 8.2 Request Flow |
| **Acceptance Criteria** | <ul><li>[ ] POST endpoint created at `/api/v1/ai/chat`</li><li>[ ] Endpoint requires authentication (uses existing auth middleware)</li><li>[ ] Request body accepts AIRequest schema</li><li>[ ] Response returns AIResponse schema</li><li>[ ] AI model called with system prompt + user message + current tasks</li><li>[ ] User's auth cookie passed through for task API calls</li><li>[ ] Endpoint returns 401 for unauthenticated requests</li><li>[ ] Loading state handled with async processing</li></ul> |

---

### P3-T05: Intent Validation & Routing

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T05 |
| **Order** | 5 |
| **Description** | Implement intent classification validation and routing logic. Parse AI model responses, validate intent type, and route to appropriate task operation handlers. |
| **Dependencies** | P3-T04 |
| **Spec References** | FR-305, FR-306, FR-307, FR-308, AIR-006 to AIR-010 |
| **Acceptance Criteria** | <ul><li>[ ] Intent classifier validates AI response matches expected schema</li><li>[ ] Router maps intents to task operations (CREATE→POST, LIST→GET, etc.)</li><li>[ ] CLARIFY intent returns clarification message without API call</li><li>[ ] ERROR intent returns error message without API call</li><li>[ ] Task reference operations (COMPLETE, UPDATE, DELETE) fetch task list first</li><li>[ ] Ambiguous task references trigger clarification flow</li><li>[ ] Invalid intents logged and return generic error</li></ul> |

---

### P3-T06: Task API Integration

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T06 |
| **Order** | 6 |
| **Description** | Implement internal API client that calls existing `/api/v1/tasks` endpoints on behalf of the user. Handle all CRUD operations with proper auth passthrough. |
| **Dependencies** | P3-T05 |
| **Spec References** | FR-313 to FR-318, Section 8.1 Endpoint Access Matrix, Section 8.3 Auth Passthrough |
| **Acceptance Criteria** | <ul><li>[ ] Internal HTTP client created for task API calls</li><li>[ ] CREATE operation calls POST /api/v1/tasks with extracted title</li><li>[ ] LIST operation calls GET /api/v1/tasks with optional completed filter</li><li>[ ] COMPLETE operation calls POST /api/v1/tasks/{id}/complete</li><li>[ ] UNCOMPLETE operation calls POST /api/v1/tasks/{id}/uncomplete</li><li>[ ] UPDATE operation calls PATCH /api/v1/tasks/{id} with new title</li><li>[ ] DELETE operation calls DELETE /api/v1/tasks/{id} after confirmation</li><li>[ ] All calls pass user's auth cookie</li><li>[ ] API responses transformed to human-readable messages</li></ul> |

---

### P3-T07: Security & Rate Limiting

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T07 |
| **Order** | 7 |
| **Description** | Implement security controls and rate limiting for AI endpoint. Add input sanitization, injection pattern detection, and rate limit enforcement. |
| **Dependencies** | P3-T06 |
| **Spec References** | SEC-301 to SEC-312, PRI-301 to PRI-304, FR-312 |
| **Acceptance Criteria** | <ul><li>[ ] Input sanitization strips dangerous characters before processing</li><li>[ ] SQL/code injection patterns detected and rejected (SEC-310)</li><li>[ ] Message length limit enforced (10000 chars max)</li><li>[ ] Task title length limit enforced (500 chars per SEC-311)</li><li>[ ] AI endpoint subject to user's existing rate limits</li><li>[ ] Rate limit errors return friendly message (429 response)</li><li>[ ] No user credentials logged (SEC-303, PRI-304)</li><li>[ ] Task content not logged (PRI-301)</li><li>[ ] Output properly escaped (SEC-312)</li></ul> |

---

### P3-T08: Frontend AI Chat UI (Full Screen)

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T08 |
| **Order** | 8 |
| **Description** | Create full-screen AI chat interface component in Next.js. Implement message display, input field, send button, and conversation history within session. |
| **Dependencies** | P3-T04 |
| **Spec References** | FR-301, FR-302, FR-303, FR-304, NFR-302 |
| **Acceptance Criteria** | <ul><li>[ ] Full-screen chat page created at `/assistant` route</li><li>[ ] Chat accessible only to authenticated users (redirect to login if not)</li><li>[ ] Message input field with send button</li><li>[ ] User messages displayed with distinct styling (right-aligned, user color)</li><li>[ ] AI responses displayed with distinct styling (left-aligned, AI color)</li><li>[ ] Conversation history maintained in session state</li><li>[ ] History cleared on logout (FR-304)</li><li>[ ] Loading indicator shown while AI processes (FR-303)</li><li>[ ] Input disabled during AI processing</li><li>[ ] Navigation link to chat from main dashboard</li></ul> |

---

### P3-T09: Dark/Light Mode Support

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T09 |
| **Order** | 9 |
| **Description** | Implement dark/light mode toggle for AI chat interface. Ensure all chat components respect system preference and manual toggle. |
| **Dependencies** | P3-T08 |
| **Spec References** | NFR-311 (usability) |
| **Acceptance Criteria** | <ul><li>[ ] Theme toggle button in chat header</li><li>[ ] System preference detected on initial load</li><li>[ ] User preference persisted in localStorage</li><li>[ ] All chat components styled for both themes</li><li>[ ] Message bubbles have appropriate contrast in both modes</li><li>[ ] Loading indicators visible in both modes</li><li>[ ] Input field styled for both modes</li><li>[ ] Theme transition smooth (no flash)</li></ul> |

---

### P3-T10: Animations & UX Polish

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T10 |
| **Order** | 10 |
| **Description** | Add smooth animations and UX polish to chat interface. Implement message appear animations, typing indicators, scroll behavior, and micro-interactions. |
| **Dependencies** | P3-T09 |
| **Spec References** | NFR-302, NFR-311, NFR-312 |
| **Acceptance Criteria** | <ul><li>[ ] New messages animate in with fade/slide effect</li><li>[ ] Typing indicator shown while AI is processing</li><li>[ ] Auto-scroll to latest message on new message</li><li>[ ] Smooth scroll behavior when scrolling history</li><li>[ ] Send button has hover/active states</li><li>[ ] Input focus ring styled appropriately</li><li>[ ] Message timestamps displayed (optional hover)</li><li>[ ] Empty state with helpful prompt when no messages</li><li>[ ] Animations don't cause layout shift</li></ul> |

---

### P3-T11: Frontend Error Handling

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T11 |
| **Order** | 11 |
| **Description** | Implement comprehensive error handling in frontend chat component. Display user-friendly error messages, handle network failures, and implement graceful degradation. |
| **Dependencies** | P3-T10 |
| **Spec References** | FR-323, FR-324, FR-325, NFR-304, NFR-305, Section 10.3 |
| **Acceptance Criteria** | <ul><li>[ ] Network errors display retry message</li><li>[ ] 401 errors redirect to login with message</li><li>[ ] 429 rate limit errors display wait message</li><li>[ ] 500/503 errors display generic error with retry suggestion</li><li>[ ] AI service unavailable shows fallback message</li><li>[ ] Error messages styled distinctly (error color)</li><li>[ ] Errors don't crash the chat component</li><li>[ ] Link to standard task UI provided on AI unavailability</li><li>[ ] No stack traces or technical details exposed to user</li></ul> |

---

### P3-T12: Backend Error Handling

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T12 |
| **Order** | 12 |
| **Description** | Implement comprehensive error handling in backend AI endpoint. Map all error types to user-friendly responses, implement timeouts, and handle AI model failures. |
| **Dependencies** | P3-T07 |
| **Spec References** | FR-323, FR-324, FR-325, Section 10.1, Section 10.2 |
| **Acceptance Criteria** | <ul><li>[ ] AI model timeout (10s) returns friendly timeout message</li><li>[ ] AI model errors return generic error (no details exposed)</li><li>[ ] Task API 404 returns "task not found" with suggestion</li><li>[ ] Task API 403 returns "access denied" message</li><li>[ ] Task API 400 returns specific validation error</li><li>[ ] All errors follow AIResponse schema with intent=ERROR</li><li>[ ] Errors include recoverable flag and suggestion</li><li>[ ] Errors logged without PII</li><li>[ ] AI model rate limits handled gracefully</li></ul> |

---

### P3-T13: Unit & Integration Tests

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T13 |
| **Order** | 13 |
| **Description** | Write comprehensive unit and integration tests for AI assistant. Cover intent classification, API integration, security controls, and error handling. |
| **Dependencies** | P3-T11, P3-T12 |
| **Spec References** | SC-301 to SC-315, Section 12.1 Mandatory Deliverables |
| **Acceptance Criteria** | <ul><li>[ ] Unit tests for intent schema validation</li><li>[ ] Unit tests for prompt contract (system prompt present)</li><li>[ ] Unit tests for input sanitization</li><li>[ ] Unit tests for each intent type routing</li><li>[ ] Integration tests for AI endpoint authentication</li><li>[ ] Integration tests for CREATE intent → task created</li><li>[ ] Integration tests for LIST intent → tasks returned</li><li>[ ] Integration tests for COMPLETE intent → task completed</li><li>[ ] Integration tests for DELETE intent → confirmation flow</li><li>[ ] Integration tests for out-of-scope requests → error response</li><li>[ ] Tests for hallucination prevention (non-existent task ID)</li><li>[ ] All Phase I tests still pass</li><li>[ ] All Phase II tests still pass</li></ul> |

---

### P3-T14: End-to-End Verification

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T14 |
| **Order** | 14 |
| **Description** | Perform end-to-end verification of all success criteria. Run through all judge-verifiable scenarios and document results. |
| **Dependencies** | P3-T13 |
| **Spec References** | SC-301 to SC-315, Section 12.3 Acceptance Gate |
| **Acceptance Criteria** | <ul><li>[ ] SC-301: Create task via "Create task Test" → task appears ✓</li><li>[ ] SC-302: List tasks via "Show my tasks" → list returned ✓</li><li>[ ] SC-303: Complete task via natural language → status changed ✓</li><li>[ ] SC-304: Delete task via natural language → confirmation → removed ✓</li><li>[ ] SC-305: Update task title via natural language → title changed ✓</li><li>[ ] SC-306: All responses are structured JSON ✓</li><li>[ ] SC-307: "What's the weather?" → scope error ✓</li><li>[ ] SC-308: Unauthenticated request → 401 ✓</li><li>[ ] SC-309: Cross-user access → 403 ✓</li><li>[ ] SC-310: Non-existent task ID → proper error ✓</li><li>[ ] SC-311: Phase II test suite passes ✓</li><li>[ ] SC-312: Phase I test suite passes ✓</li><li>[ ] SC-313: Cookie-based auth verified ✓</li><li>[ ] SC-314: 95% requests under 10s ✓</li><li>[ ] SC-315: UI responsive during processing ✓</li><li>[ ] Verification results documented in `verification-report.md`</li></ul> |

---

### P3-T15: Git Tagging & Submission

| Attribute | Value |
|-----------|-------|
| **Task ID** | P3-T15 |
| **Order** | 15 |
| **Description** | Create git tag for Phase 3 completion, update documentation, and prepare submission package. |
| **Dependencies** | P3-T14 |
| **Spec References** | Section 12.2 Definition of Done Checklist |
| **Acceptance Criteria** | <ul><li>[ ] All code committed to branch `001-ai-assistant-integration`</li><li>[ ] Definition of Done checklist completed (all items checked)</li><li>[ ] Git tag created: `v3.0.0-phase3-ai-assistant`</li><li>[ ] Tag message includes: Phase 3 features summary, verification status</li><li>[ ] README updated with Phase 3 features and usage</li><li>[ ] Environment variables documented</li><li>[ ] Branch merged to main (or PR created)</li><li>[ ] No secrets committed to repository</li><li>[ ] Submission package ready for judge review</li></ul> |

---

## Task Summary Table

| Task ID | Description | Order | Dependencies | Est. Complexity |
|---------|-------------|-------|--------------|-----------------|
| P3-T01 | AI Prompt Contract Creation | 1 | None | Medium |
| P3-T02 | Intent Schema Definition | 2 | P3-T01 | Medium |
| P3-T03 | Environment Configuration | 3 | None | Low |
| P3-T04 | Backend AI Endpoint | 4 | P3-T01, P3-T02, P3-T03 | High |
| P3-T05 | Intent Validation & Routing | 5 | P3-T04 | High |
| P3-T06 | Task API Integration | 6 | P3-T05 | High |
| P3-T07 | Security & Rate Limiting | 7 | P3-T06 | Medium |
| P3-T08 | Frontend Chat UI (Full Screen) | 8 | P3-T04 | High |
| P3-T09 | Dark/Light Mode Support | 9 | P3-T08 | Low |
| P3-T10 | Animations & UX Polish | 10 | P3-T09 | Medium |
| P3-T11 | Frontend Error Handling | 11 | P3-T10 | Medium |
| P3-T12 | Backend Error Handling | 12 | P3-T07 | Medium |
| P3-T13 | Unit & Integration Tests | 13 | P3-T11, P3-T12 | High |
| P3-T14 | End-to-End Verification | 14 | P3-T13 | Medium |
| P3-T15 | Git Tagging & Submission | 15 | P3-T14 | Low |

---

## Critical Path

The critical path for Phase 3 delivery is:

```
T01 → T02 → T04 → T05 → T06 → T07 → T12 → T13 → T14 → T15
```

Frontend tasks (T08-T11) can be developed in parallel with backend tasks (T05-T07, T12) after T04 is complete.

---

## Risk Mitigation Tasks

| Risk | Mitigation Task |
|------|-----------------|
| AI model latency | T04: Implement 10s timeout with fallback |
| AI hallucination | T05: Mandatory task list refresh before ID operations |
| Prompt injection | T07: Input sanitization and pattern detection |
| Auth bypass | T07: Verify cookie passthrough in all API calls |
| UX degradation | T11: Graceful degradation with link to standard UI |

---

## Verification Checklist Mapping

| Success Criterion | Verified By Task |
|-------------------|------------------|
| SC-301 to SC-307 | P3-T14 |
| SC-308 to SC-310 | P3-T13, P3-T14 |
| SC-311, SC-312 | P3-T13 |
| SC-313 | P3-T13, P3-T14 |
| SC-314, SC-315 | P3-T14 |
