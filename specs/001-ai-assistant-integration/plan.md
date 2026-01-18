# Phase 3 Execution Plan: AI Assistant Integration

**Feature Branch**: `001-ai-assistant-integration`
**Created**: 2026-01-13
**Status**: Ready for Implementation
**Specification**: [spec.md](./spec.md)
**Tasks**: [tasks.md](./tasks.md)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Phase 2 Baseline (DO NOT MODIFY)](#2-phase-2-baseline-do-not-modify)
3. [Backend Implementation Plan](#3-backend-implementation-plan)
4. [Frontend Implementation Plan](#4-frontend-implementation-plan)
5. [AI Prompt Flow Architecture](#5-ai-prompt-flow-architecture)
6. [Security Layers](#6-security-layers)
7. [Error Flow Architecture](#7-error-flow-architecture)
8. [Testing Approach](#8-testing-approach)
9. [Step-by-Step Implementation Roadmap](#9-step-by-step-implementation-roadmap)
10. [File Change Summary](#10-file-change-summary)

---

## 1. Executive Summary

This plan details the implementation of Phase 3 AI Assistant Integration for PakAura. The AI assistant provides a natural language interface for task management while maintaining full backward compatibility with Phase 1 CLI and Phase 2 web application.

**Core Architecture Decision**: The AI assistant operates as a proxy layer that translates natural language into existing API calls. It has NO direct database access and relies entirely on the existing `/api/v1/tasks` endpoints.

**Key Constraints**:
- Phase 2 code remains unchanged (no modifications to existing files)
- AI uses existing authentication system (JWT cookies)
- All AI operations go through existing task API endpoints
- No new database tables or schema changes

---

## 2. Phase 2 Baseline (DO NOT MODIFY)

The following files and directories are part of Phase 2 and **MUST NOT be modified**:

### Backend Files (Protected)
```
api/src/
├── config.py                    # ✗ DO NOT MODIFY
├── main.py                      # ✓ ADD router only (line ~93)
├── db/
│   ├── connection.py            # ✗ DO NOT MODIFY
│   └── migrations/              # ✗ DO NOT MODIFY
├── middleware/
│   ├── auth.py                  # ✗ DO NOT MODIFY (import only)
│   └── rate_limit.py            # ✗ DO NOT MODIFY
├── models/
│   ├── base.py                  # ✗ DO NOT MODIFY
│   ├── user.py                  # ✗ DO NOT MODIFY
│   └── task.py                  # ✗ DO NOT MODIFY
├── routes/
│   ├── __init__.py              # ✓ ADD ai router import
│   ├── auth.py                  # ✗ DO NOT MODIFY
│   └── tasks.py                 # ✗ DO NOT MODIFY
├── schemas/
│   ├── auth.py                  # ✗ DO NOT MODIFY
│   ├── task.py                  # ✗ DO NOT MODIFY
│   └── common.py                # ✗ DO NOT MODIFY
└── services/
    ├── auth_service.py          # ✗ DO NOT MODIFY
    └── task_service.py          # ✗ DO NOT MODIFY (import only)
```

### Frontend Files (Protected)
```
frontend/src/
├── app/
│   ├── layout.tsx               # ✗ DO NOT MODIFY
│   ├── page.tsx                 # ✗ DO NOT MODIFY
│   ├── (auth)/                  # ✗ DO NOT MODIFY
│   └── (protected)/
│       ├── layout.tsx           # ✗ DO NOT MODIFY
│       └── dashboard/           # ✗ DO NOT MODIFY
├── components/
│   ├── ui/                      # ✗ DO NOT MODIFY (import only)
│   ├── auth/                    # ✗ DO NOT MODIFY
│   ├── tasks/                   # ✗ DO NOT MODIFY
│   └── providers/               # ✗ DO NOT MODIFY
├── lib/
│   ├── api.ts                   # ✗ DO NOT MODIFY (import only)
│   ├── auth.ts                  # ✗ DO NOT MODIFY (import only)
│   └── validation.ts            # ✗ DO NOT MODIFY
├── types/
│   ├── auth.ts                  # ✗ DO NOT MODIFY
│   └── task.ts                  # ✗ DO NOT MODIFY (import only)
└── middleware.ts                # ✓ ADD /assistant route protection
```

---

## 3. Backend Implementation Plan

### 3.1 New Directory Structure

```
api/src/
├── ai/                          # NEW DIRECTORY
│   ├── __init__.py              # Module exports
│   ├── prompts.py               # System prompt and templates (P3-T01)
│   ├── schemas.py               # AI request/response schemas (P3-T02)
│   ├── client.py                # AI model API client (P3-T04)
│   ├── intent_router.py         # Intent classification and routing (P3-T05)
│   ├── task_executor.py         # Task API integration (P3-T06)
│   ├── sanitizer.py             # Input sanitization (P3-T07)
│   └── errors.py                # AI-specific error handling (P3-T12)
└── routes/
    └── ai.py                    # AI chat endpoint (P3-T04)
```

### 3.2 File Specifications

#### `api/src/ai/__init__.py`
```python
"""AI Assistant module for PakAura Phase 3."""
from .schemas import AIRequest, AIResponse, Intent, ActionType
from .client import AIClient
from .intent_router import IntentRouter
from .task_executor import TaskExecutor
from .sanitizer import InputSanitizer
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

__all__ = [
    "AIRequest", "AIResponse", "Intent", "ActionType",
    "AIClient", "IntentRouter", "TaskExecutor",
    "InputSanitizer", "SYSTEM_PROMPT", "USER_PROMPT_TEMPLATE"
]
```

#### `api/src/ai/prompts.py` (P3-T01)
**Purpose**: Define system prompt and user prompt templates

**Contents**:
- `SYSTEM_PROMPT`: Full system prompt from spec Section 7.1
- `USER_PROMPT_TEMPLATE`: Template with placeholders for user_input and current_tasks
- `CLARIFY_RESPONSE`: Pre-defined clarification response template
- `ERROR_RESPONSE`: Pre-defined error response template
- `SCOPE_ERROR_RESPONSE`: Response for out-of-scope requests

**Key Implementation Details**:
- System prompt embeds all AIR rules (001-020)
- Response format enforced via prompt
- Strict JSON output format specified
- No hallucination instructions embedded

#### `api/src/ai/schemas.py` (P3-T02)
**Purpose**: Define Pydantic models for AI request/response

**Models**:
```python
class Intent(str, Enum):
    CREATE = "CREATE"
    LIST = "LIST"
    COMPLETE = "COMPLETE"
    UNCOMPLETE = "UNCOMPLETE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CLARIFY = "CLARIFY"
    ERROR = "ERROR"
    INFO = "INFO"

class ActionType(str, Enum):
    API_CALL = "api_call"
    NONE = "none"

class AIAction(BaseModel):
    type: ActionType
    endpoint: Optional[str] = None
    method: Optional[str] = None
    payload: Optional[dict] = None

class AIRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None

class AIResponse(BaseModel):
    intent: Intent
    message: str
    action: AIAction
    data: Optional[dict] = None

class AIErrorData(BaseModel):
    error_code: str
    recoverable: bool
    suggestion: Optional[str] = None
```

#### `api/src/ai/client.py` (P3-T04)
**Purpose**: AI model API client wrapper

**Class**: `AIClient`
**Methods**:
- `__init__(api_key: str, model: str, timeout: int)`
- `async chat(system_prompt: str, user_message: str) -> dict`
- `_parse_response(raw_response: str) -> AIResponse`

**Implementation Details**:
- Uses httpx async client for API calls
- 10-second timeout (configurable via env)
- Handles API rate limits with retry backoff
- Parses JSON response from AI model
- Raises `AIModelError` on failures

#### `api/src/ai/intent_router.py` (P3-T05)
**Purpose**: Route AI intents to appropriate handlers

**Class**: `IntentRouter`
**Methods**:
- `async route(ai_response: AIResponse, user_id: UUID, db: AsyncSession) -> AIResponse`
- `_handle_create(payload: dict, user_id: UUID, db: AsyncSession) -> AIResponse`
- `_handle_list(payload: dict, user_id: UUID, db: AsyncSession) -> AIResponse`
- `_handle_complete(task_id: UUID, user_id: UUID, db: AsyncSession) -> AIResponse`
- `_handle_uncomplete(task_id: UUID, user_id: UUID, db: AsyncSession) -> AIResponse`
- `_handle_update(task_id: UUID, payload: dict, user_id: UUID, db: AsyncSession) -> AIResponse`
- `_handle_delete(task_id: UUID, user_id: UUID, db: AsyncSession) -> AIResponse`
- `_handle_clarify(ai_response: AIResponse) -> AIResponse`
- `_handle_error(ai_response: AIResponse) -> AIResponse`

**Implementation Details**:
- Validates intent before routing
- Fetches task list for reference operations
- Verifies task IDs exist before operations
- Transforms API responses to human-readable messages

#### `api/src/ai/task_executor.py` (P3-T06)
**Purpose**: Execute task operations via existing TaskService

**Class**: `TaskExecutor`
**Methods**:
- `async create_task(title: str, user_id: UUID, db: AsyncSession) -> Task`
- `async list_tasks(user_id: UUID, db: AsyncSession, completed: Optional[bool]) -> List[Task]`
- `async complete_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> Task`
- `async uncomplete_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> Task`
- `async update_task(task_id: UUID, title: str, user_id: UUID, db: AsyncSession) -> Task`
- `async delete_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> bool`
- `async get_task(task_id: UUID, user_id: UUID, db: AsyncSession) -> Task`
- `_format_task_message(task: Task, operation: str) -> str`
- `_format_task_list_message(tasks: List[Task]) -> str`

**Implementation Details**:
- Imports and uses existing `TaskService` from `services.task_service`
- NO direct database queries (uses service layer)
- Formats responses with human-readable messages
- Handles `NotFoundError` and `AuthorizationError` from TaskService

#### `api/src/ai/sanitizer.py` (P3-T07)
**Purpose**: Input sanitization and security checks

**Class**: `InputSanitizer`
**Methods**:
- `sanitize(message: str) -> str`
- `check_injection_patterns(message: str) -> bool`
- `validate_length(message: str, max_length: int) -> bool`
- `escape_output(text: str) -> str`

**Patterns to Detect**:
```python
INJECTION_PATTERNS = [
    r"(?i)(select|insert|update|delete|drop|union|exec|execute)\s",
    r"(?i)(script|javascript|onclick|onerror)",
    r"[<>\"']",  # HTML/XSS characters
    r"(?i)(rm\s+-rf|wget|curl.*\||eval\()",
    r"[\x00-\x1f]",  # Control characters
]
```

#### `api/src/ai/errors.py` (P3-T12)
**Purpose**: AI-specific error handling

**Classes**:
```python
class AIModelError(Exception):
    """AI model API error"""
    pass

class AITimeoutError(AIModelError):
    """AI model timeout"""
    pass

class AIRateLimitError(AIModelError):
    """AI model rate limited"""
    pass

class AIParseError(AIModelError):
    """Failed to parse AI response"""
    pass
```

**Functions**:
- `create_error_response(error_code: str, message: str, suggestion: str) -> AIResponse`
- `map_task_error_to_response(error: Exception) -> AIResponse`
- `map_ai_error_to_response(error: AIModelError) -> AIResponse`

#### `api/src/routes/ai.py` (P3-T04)
**Purpose**: FastAPI router for AI chat endpoint

**Endpoint**: `POST /api/v1/ai/chat`

```python
@router.post("/chat", response_model=AIResponse)
async def chat(
    request: AIRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AIResponse:
    """
    Process natural language message and return AI response.

    FR-301: Authenticated users only
    FR-309: Uses existing task endpoints
    FR-310: User auth context preserved
    """
```

**Flow**:
1. Validate request (sanitize input)
2. Fetch current user's tasks
3. Build user prompt with tasks context
4. Call AI model
5. Parse and validate response
6. Route intent to handler
7. Return formatted response

### 3.3 Configuration Updates

#### `api/src/config.py` (ADD to existing, P3-T03)
```python
# AI Configuration (ADD these fields to Settings class)
ai_api_key: str = Field(default="", env="AI_API_KEY")
ai_model_name: str = Field(default="claude-3-haiku-20240307", env="AI_MODEL_NAME")
ai_timeout_seconds: int = Field(default=10, env="AI_TIMEOUT_SECONDS")
ai_max_message_length: int = Field(default=10000, env="AI_MAX_MESSAGE_LENGTH")
```

#### `api/.env.example` (UPDATE)
```
# AI Configuration (Phase 3)
AI_API_KEY=your-ai-api-key-here
AI_MODEL_NAME=claude-3-haiku-20240307
AI_TIMEOUT_SECONDS=10
AI_MAX_MESSAGE_LENGTH=10000
```

### 3.4 Router Registration

#### `api/src/routes/__init__.py` (UPDATE)
```python
# ADD import
from .ai import router as ai_router

# ADD to api_router
api_router.include_router(ai_router, prefix="/ai", tags=["AI Assistant"])
```

---

## 4. Frontend Implementation Plan

### 4.1 New Directory Structure

```
frontend/src/
├── app/
│   └── (protected)/
│       └── assistant/           # NEW DIRECTORY
│           └── page.tsx         # AI chat page (P3-T08)
├── components/
│   └── assistant/               # NEW DIRECTORY
│       ├── index.ts             # Component exports
│       ├── ChatContainer.tsx    # Main chat container (P3-T08)
│       ├── MessageList.tsx      # Message display list (P3-T08)
│       ├── MessageBubble.tsx    # Individual message bubble (P3-T08)
│       ├── ChatInput.tsx        # Message input field (P3-T08)
│       ├── TypingIndicator.tsx  # AI typing indicator (P3-T10)
│       ├── EmptyState.tsx       # Empty chat state (P3-T10)
│       └── ErrorMessage.tsx     # Error display (P3-T11)
├── lib/
│   └── assistant.ts             # AI API client (P3-T08)
└── types/
    └── ai.ts                    # AI types (P3-T02)
```

### 4.2 File Specifications

#### `frontend/src/types/ai.ts` (P3-T02)
```typescript
export type Intent =
  | "CREATE"
  | "LIST"
  | "COMPLETE"
  | "UNCOMPLETE"
  | "UPDATE"
  | "DELETE"
  | "CLARIFY"
  | "ERROR"
  | "INFO";

export type ActionType = "api_call" | "none";

export interface AIAction {
  type: ActionType;
  endpoint?: string;
  method?: string;
  payload?: Record<string, unknown>;
}

export interface AIRequest {
  message: string;
  conversation_id?: string;
}

export interface AIResponse {
  intent: Intent;
  message: string;
  action: AIAction;
  data?: Record<string, unknown> | null;
}

export interface AIErrorData {
  error_code: string;
  recoverable: boolean;
  suggestion?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  intent?: Intent;
  data?: Record<string, unknown> | null;
}
```

#### `frontend/src/lib/assistant.ts` (P3-T08)
```typescript
import { api } from "./api";
import type { AIRequest, AIResponse } from "@/types/ai";

export async function sendMessage(message: string): Promise<AIResponse> {
  const request: AIRequest = { message };
  return api.post<AIResponse>("/api/v1/ai/chat", request);
}

export function formatTasksForDisplay(data: Record<string, unknown>): string {
  // Format task data for display in chat
}

export function isErrorResponse(response: AIResponse): boolean {
  return response.intent === "ERROR";
}
```

#### `frontend/src/app/(protected)/assistant/page.tsx` (P3-T08)
```typescript
"use client";

import { ChatContainer } from "@/components/assistant";

export default function AssistantPage() {
  return (
    <div className="h-screen flex flex-col">
      <ChatContainer />
    </div>
  );
}
```

#### `frontend/src/components/assistant/ChatContainer.tsx` (P3-T08)
**Purpose**: Main container managing chat state

**State**:
- `messages: ChatMessage[]` - Conversation history
- `isLoading: boolean` - AI processing state
- `error: string | null` - Error state

**Methods**:
- `handleSendMessage(message: string)` - Send message to AI
- `handleClearHistory()` - Clear conversation (FR-304)

**Structure**:
```tsx
<div className="flex flex-col h-full">
  <ChatHeader onClear={handleClearHistory} />
  <MessageList messages={messages} isLoading={isLoading} />
  <ChatInput onSend={handleSendMessage} disabled={isLoading} />
</div>
```

#### `frontend/src/components/assistant/MessageBubble.tsx` (P3-T08)
**Purpose**: Individual message display

**Props**:
- `message: ChatMessage`
- `isUser: boolean`

**Styling** (P3-T09 Dark/Light Mode):
```tsx
// User message (right-aligned)
const userStyles = "ml-auto bg-blue-500 text-white dark:bg-blue-600";

// AI message (left-aligned)
const aiStyles = "mr-auto bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100";
```

#### `frontend/src/components/assistant/TypingIndicator.tsx` (P3-T10)
**Purpose**: Animated typing indicator during AI processing

**Animation**: Three bouncing dots using Framer Motion

#### `frontend/src/components/assistant/ErrorMessage.tsx` (P3-T11)
**Purpose**: Error display with retry option

**Props**:
- `error: string`
- `onRetry?: () => void`
- `showFallbackLink?: boolean`

**Display**:
```tsx
<div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
  <p className="text-red-700 dark:text-red-300">{error}</p>
  {showFallbackLink && (
    <Link href="/dashboard">Use standard task manager</Link>
  )}
</div>
```

### 4.3 Middleware Update

#### `frontend/src/middleware.ts` (UPDATE)
```typescript
// ADD to protectedPaths array
const protectedPaths = ["/dashboard", "/assistant"];
```

### 4.4 Navigation Update

Add navigation link to assistant page from dashboard:

```tsx
// In dashboard or header component
<Link href="/assistant" className="...">
  <SparklesIcon className="w-5 h-5" />
  AI Assistant
</Link>
```

---

## 5. AI Prompt Flow Architecture

### 5.1 Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  User Input: "Add task to buy groceries"                                │
│       ↓                                                                 │
│  ChatContainer.handleSendMessage()                                      │
│       ↓                                                                 │
│  POST /api/v1/ai/chat { message: "Add task to buy groceries" }         │
│       + Cookie: auth_token=<jwt>                                        │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND                                        │
├─────────────────────────────────────────────────────────────────────────┤
│  1. Authentication Check (get_current_user)                             │
│       ↓                                                                 │
│  2. Input Sanitization (InputSanitizer.sanitize)                        │
│       ↓                                                                 │
│  3. Fetch Current Tasks (TaskService.list)                              │
│       ↓                                                                 │
│  4. Build Prompt                                                        │
│     ┌──────────────────────────────────────────────────────────────┐   │
│     │ SYSTEM_PROMPT (from prompts.py)                               │   │
│     │ +                                                             │   │
│     │ USER_PROMPT_TEMPLATE.format(                                  │   │
│     │   user_input="Add task to buy groceries",                     │   │
│     │   current_tasks=[{id: "abc", title: "existing task"}, ...]   │   │
│     │ )                                                             │   │
│     └──────────────────────────────────────────────────────────────┘   │
│       ↓                                                                 │
│  5. Call AI Model (AIClient.chat)                                       │
│       ↓                                                                 │
│  6. Parse Response to AIResponse schema                                 │
│       ↓                                                                 │
│  7. Route Intent (IntentRouter.route)                                   │
│       ↓                                                                 │
│  8. Execute Task Operation (TaskExecutor)                               │
│       ↓                                                                 │
│  9. Return AIResponse                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Response: {                                                            │
│    intent: "CREATE",                                                    │
│    message: "I've created a task 'buy groceries' for you.",            │
│    action: { type: "api_call", endpoint: "/tasks", method: "POST" },   │
│    data: { task: { id: "xyz", title: "buy groceries", ... } }          │
│  }                                                                      │
│       ↓                                                                 │
│  Display AI response in MessageBubble                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Intent Processing Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AI Model Response                                    │
│  { intent: "COMPLETE", message: "...", action: {...}, data: {...} }    │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                     IntentRouter.route()                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  switch(intent):                                                        │
│    CREATE     → TaskExecutor.create_task()     → POST /tasks           │
│    LIST       → TaskExecutor.list_tasks()      → GET /tasks            │
│    COMPLETE   → TaskExecutor.complete_task()   → POST /tasks/{id}/complete │
│    UNCOMPLETE → TaskExecutor.uncomplete_task() → POST /tasks/{id}/uncomplete │
│    UPDATE     → TaskExecutor.update_task()     → PATCH /tasks/{id}     │
│    DELETE     → TaskExecutor.delete_task()     → DELETE /tasks/{id}    │
│    CLARIFY    → Return clarification message   → No API call           │
│    ERROR      → Return error message           → No API call           │
│    INFO       → Return info message            → No API call           │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Task Reference Resolution

For operations requiring task reference (COMPLETE, UPDATE, DELETE):

```
User: "Mark the grocery task as done"
                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  AI Model analyzes message with CURRENT_TASKS context                   │
│  CURRENT_TASKS: [                                                       │
│    { id: "uuid-1", title: "buy groceries", completed: false },         │
│    { id: "uuid-2", title: "call mom", completed: true }                │
│  ]                                                                      │
│                    ↓                                                    │
│  AI identifies "grocery task" matches "buy groceries" (uuid-1)         │
│                    ↓                                                    │
│  Response: {                                                            │
│    intent: "COMPLETE",                                                  │
│    action: {                                                            │
│      type: "api_call",                                                  │
│      endpoint: "/tasks/uuid-1/complete",                                │
│      method: "POST"                                                     │
│    }                                                                    │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.4 Ambiguity Resolution

```
User: "Complete the task"
                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  AI Model cannot determine which task (multiple incomplete tasks)       │
│                    ↓                                                    │
│  Response: {                                                            │
│    intent: "CLARIFY",                                                   │
│    message: "Which task would you like to complete? You have:\n"       │
│             "1. buy groceries\n"                                        │
│             "2. call mom",                                              │
│    action: { type: "none" },                                            │
│    data: null                                                           │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Security Layers

### 6.1 Security Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         REQUEST ENTRY                                    │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: Rate Limiting (Existing Phase 2)                              │
│  ─────────────────────────────────────────                              │
│  • 100 requests/min per IP for task endpoints                           │
│  • AI endpoint inherits same rate limits                                │
│  • Returns 429 with Retry-After header                                  │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: Authentication (Existing Phase 2)                             │
│  ─────────────────────────────────────────                              │
│  • JWT validation via get_current_user dependency                       │
│  • Cookie-based authentication (auth_token)                             │
│  • Returns 401 for invalid/missing token                                │
│  • NO modifications - reuse existing middleware                         │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: Input Sanitization (NEW - P3-T07)                             │
│  ─────────────────────────────────────────                              │
│  • Message length validation (max 10000 chars)                          │
│  • Injection pattern detection (SQL, XSS, shell)                        │
│  • Control character stripping                                          │
│  • Returns 400 with error details                                       │
│                                                                         │
│  Implementation: InputSanitizer.sanitize()                              │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: AI Prompt Security (NEW - P3-T01)                             │
│  ─────────────────────────────────────────                              │
│  • System prompt enforces scope boundaries                              │
│  • Task-only operations allowed                                         │
│  • No system architecture disclosure                                    │
│  • No other user data access                                            │
│                                                                         │
│  Implementation: SYSTEM_PROMPT with strict rules                        │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: Authorization (Existing Phase 2)                              │
│  ─────────────────────────────────────────                              │
│  • Task operations scoped to current user                               │
│  • TaskService enforces user_id filtering                               │
│  • Returns 403 for cross-user access attempts                           │
│  • NO modifications - reuse existing service layer                      │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 6: Output Sanitization (NEW - P3-T07)                            │
│  ─────────────────────────────────────────                              │
│  • HTML entity escaping                                                 │
│  • Response validation against schema                                   │
│  • No internal error details exposed                                    │
│                                                                         │
│  Implementation: InputSanitizer.escape_output()                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Security Controls Mapping

| Control | Spec Reference | Implementation Location |
|---------|----------------|------------------------|
| Auth required | SEC-301, SEC-304 | `routes/ai.py` - get_current_user dependency |
| No token manipulation | SEC-302 | N/A - AI doesn't touch tokens |
| No credential caching | SEC-303 | N/A - AI stateless |
| User task isolation | SEC-305 | TaskService (existing) |
| No auth bypass | SEC-306 | All operations via TaskService |
| API-level authorization | SEC-307 | TaskService (existing) |
| No auth error details | SEC-308 | errors.py - generic messages |
| Input sanitization | SEC-309 | sanitizer.py - sanitize() |
| Injection rejection | SEC-310 | sanitizer.py - check_injection_patterns() |
| Length limits | SEC-311 | schemas.py - AIRequest validation |
| Output escaping | SEC-312 | sanitizer.py - escape_output() |

### 6.3 Privacy Controls

| Control | Spec Reference | Implementation |
|---------|----------------|----------------|
| No task content logging | PRI-301 | Structured logging without content |
| No external data transmission | PRI-302 | Only AI API calls (secured) |
| No session persistence | PRI-303 | Frontend state only |
| No PII in error logs | PRI-304 | Generic error messages |

---

## 7. Error Flow Architecture

### 7.1 Error Classification

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ERROR CATEGORIES                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  AUTHENTICATION ERRORS (401)                                 │       │
│  │  • Missing auth cookie                                       │       │
│  │  • Invalid/expired JWT                                       │       │
│  │  • User not found                                            │       │
│  │  Response: "Your session has expired. Please log in again." │       │
│  │  Action: Redirect to /login                                  │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  AUTHORIZATION ERRORS (403)                                  │       │
│  │  • Cross-user task access attempt                            │       │
│  │  Response: "I can only access your own tasks."              │       │
│  │  Action: None (continue conversation)                        │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  VALIDATION ERRORS (400)                                     │       │
│  │  • Message too long (>10000 chars)                           │       │
│  │  • Injection pattern detected                                │       │
│  │  • Task title too long (>500 chars)                          │       │
│  │  Response: Specific validation message                       │       │
│  │  Action: None (allow retry)                                  │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  NOT FOUND ERRORS (404)                                      │       │
│  │  • Task ID doesn't exist                                     │       │
│  │  Response: "I couldn't find that task. Would you like to    │       │
│  │            see your current tasks?"                          │       │
│  │  Action: None (suggest alternative)                          │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  RATE LIMIT ERRORS (429)                                     │       │
│  │  • Too many requests                                         │       │
│  │  Response: "You've made too many requests. Please wait a    │       │
│  │            moment and try again."                            │       │
│  │  Action: Include Retry-After duration                        │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  AI MODEL ERRORS (503)                                       │       │
│  │  • Timeout (>10s)                                            │       │
│  │  • Model API failure                                         │       │
│  │  • Rate limited by AI provider                               │       │
│  │  Response: "The AI assistant is temporarily unavailable.    │       │
│  │            You can still manage tasks using the standard    │       │
│  │            interface."                                       │       │
│  │  Action: Show link to /dashboard                             │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  INTERNAL ERRORS (500)                                       │       │
│  │  • Unexpected exceptions                                     │       │
│  │  • Database errors                                           │       │
│  │  Response: "Something went wrong. Please try again."        │       │
│  │  Action: Log error (no PII), return generic message          │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Error Response Format

All errors follow the AIResponse schema:

```json
{
  "intent": "ERROR",
  "message": "User-friendly error message",
  "action": {
    "type": "none"
  },
  "data": {
    "error_code": "ERROR_CODE",
    "recoverable": true,
    "suggestion": "What the user can do next"
  }
}
```

### 7.3 Error Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Error Occurs                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  Backend: errors.py                                                     │
│  ─────────────────                                                      │
│  1. Classify error type                                                 │
│  2. Map to user-friendly message                                        │
│  3. Determine if recoverable                                            │
│  4. Add suggestion                                                      │
│  5. Log error (sanitized - no PII)                                      │
│  6. Return AIResponse with intent=ERROR                                 │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend: ErrorMessage.tsx                                             │
│  ─────────────────────────                                              │
│  1. Display error message                                               │
│  2. Style with error colors                                             │
│  3. Show retry button if recoverable                                    │
│  4. Show fallback link if AI unavailable                                │
│  5. Handle auth errors with redirect                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.4 Graceful Degradation

When AI service is unavailable:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  AI Service Down                                                        │
└─────────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  Display in Chat:                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  ⚠️ AI Assistant Temporarily Unavailable                         │   │
│  │                                                                   │   │
│  │  The AI assistant is currently unavailable. You can still        │   │
│  │  manage your tasks using the standard interface.                 │   │
│  │                                                                   │   │
│  │  [Go to Task Manager] ← Link to /dashboard                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Phase 2 Dashboard remains fully functional                             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Testing Approach

### 8.1 Test Categories

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TEST PYRAMID                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                           ┌─────────┐                                   │
│                          /           \                                  │
│                         /   E2E Tests \   (P3-T14)                      │
│                        /    (Manual)   \  5 scenarios                   │
│                       /─────────────────\                               │
│                      /                   \                              │
│                     /  Integration Tests  \   (P3-T13)                  │
│                    /      (Automated)      \  15+ tests                 │
│                   /─────────────────────────\                           │
│                  /                           \                          │
│                 /      Unit Tests             \   (P3-T13)              │
│                /       (Automated)             \  30+ tests             │
│               /─────────────────────────────────\                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Unit Tests

#### Backend Unit Tests (`api/tests/unit/test_ai/`)

| Test File | Coverage |
|-----------|----------|
| `test_schemas.py` | AIRequest, AIResponse, Intent enum validation |
| `test_prompts.py` | System prompt content, template placeholders |
| `test_sanitizer.py` | Input sanitization, injection detection |
| `test_intent_router.py` | Intent routing logic (mocked AI client) |
| `test_task_executor.py` | Task operations (mocked TaskService) |
| `test_errors.py` | Error response formatting |

**Example Tests**:
```python
# test_schemas.py
def test_ai_request_validates_message_length():
    """Message must be between 1 and 10000 characters."""
    with pytest.raises(ValidationError):
        AIRequest(message="")  # Too short

    with pytest.raises(ValidationError):
        AIRequest(message="x" * 10001)  # Too long

def test_intent_enum_values():
    """All required intents must be defined."""
    assert Intent.CREATE.value == "CREATE"
    assert Intent.LIST.value == "LIST"
    # ... all 9 intents
```

```python
# test_sanitizer.py
def test_detects_sql_injection():
    """SQL injection patterns must be detected."""
    sanitizer = InputSanitizer()
    assert sanitizer.check_injection_patterns("SELECT * FROM users")
    assert sanitizer.check_injection_patterns("'; DROP TABLE tasks; --")
    assert not sanitizer.check_injection_patterns("Show my tasks")

def test_strips_control_characters():
    """Control characters must be removed."""
    sanitizer = InputSanitizer()
    result = sanitizer.sanitize("Hello\x00World")
    assert "\x00" not in result
```

#### Frontend Unit Tests (`frontend/src/__tests__/`)

| Test File | Coverage |
|-----------|----------|
| `assistant/MessageBubble.test.tsx` | User/AI styling, content display |
| `assistant/ChatInput.test.tsx` | Input validation, disabled state |
| `assistant/ErrorMessage.test.tsx` | Error display, retry button |
| `lib/assistant.test.ts` | API client functions |

### 8.3 Integration Tests

#### Backend Integration Tests (`api/tests/integration/test_ai/`)

| Test File | Coverage |
|-----------|----------|
| `test_ai_endpoint.py` | Full endpoint flow with real DB |

**Test Scenarios**:

```python
# test_ai_endpoint.py

@pytest.mark.asyncio
async def test_ai_chat_requires_auth(client):
    """Unauthenticated requests return 401."""
    response = await client.post("/api/v1/ai/chat", json={"message": "Hello"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_task_via_ai(authenticated_client, db):
    """CREATE intent creates task via TaskService."""
    response = await authenticated_client.post(
        "/api/v1/ai/chat",
        json={"message": "Add a task to buy groceries"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "CREATE"

    # Verify task was created
    tasks = await TaskService.list(db, user_id)
    assert any(t.title == "buy groceries" for t in tasks)

@pytest.mark.asyncio
async def test_list_tasks_via_ai(authenticated_client_with_tasks):
    """LIST intent returns user's tasks."""
    response = await authenticated_client_with_tasks.post(
        "/api/v1/ai/chat",
        json={"message": "Show my tasks"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "LIST"
    assert "tasks" in data["data"]

@pytest.mark.asyncio
async def test_out_of_scope_request(authenticated_client):
    """Out-of-scope requests return ERROR intent."""
    response = await authenticated_client.post(
        "/api/v1/ai/chat",
        json={"message": "What's the weather?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "ERROR"
    assert "task management" in data["message"].lower()

@pytest.mark.asyncio
async def test_nonexistent_task_reference(authenticated_client):
    """Referencing non-existent task returns proper error."""
    response = await authenticated_client.post(
        "/api/v1/ai/chat",
        json={"message": "Complete task with ID fake-uuid-1234"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "couldn't find" in data["message"].lower()
```

### 8.4 End-to-End Verification (P3-T14)

Manual verification checklist mapped to success criteria:

| SC ID | Test Case | Steps | Expected Result |
|-------|-----------|-------|-----------------|
| SC-301 | Create task | 1. Login 2. Go to /assistant 3. Type "Create task Test" 4. Submit | Task appears in list |
| SC-302 | List tasks | 1. Have tasks 2. Type "Show my tasks" | All tasks displayed |
| SC-303 | Complete task | 1. Have incomplete task 2. Type "Complete [task]" | Task marked complete |
| SC-304 | Delete task | 1. Have task 2. Type "Delete [task]" 3. Confirm | Task removed |
| SC-305 | Update task | 1. Have task 2. Type "Rename [task] to [new]" | Title changed |
| SC-306 | JSON format | Inspect all responses | All structured JSON |
| SC-307 | Scope error | Type "What's the weather?" | Error response |
| SC-308 | No auth | Call endpoint without cookie | 401 response |
| SC-309 | Cross-user | Attempt to access other's task | 403 response |
| SC-310 | No hallucination | Reference fake task ID | Proper error |
| SC-311 | Phase II tests | Run pytest | All pass |
| SC-312 | Phase I tests | Run pytest | All pass |
| SC-313 | Cookie auth | Inspect AI requests | Cookie present |
| SC-314 | Performance | Time 10 operations | 95% < 10s |
| SC-315 | UI responsive | Use chat while processing | Loading state shown |

### 8.5 Regression Testing

**Phase I Tests** (`backend/tests/`):
- All existing tests must pass
- No modifications to test files

**Phase II Tests** (`api/tests/`):
- All existing tests must pass
- No modifications to test files

**Verification Command**:
```bash
# Phase I
cd backend && python -m pytest tests/ -v

# Phase II
cd api && python -m pytest tests/ -v

# Phase III
cd api && python -m pytest tests/unit/test_ai/ tests/integration/test_ai/ -v
```

---

## 9. Step-by-Step Implementation Roadmap

### Phase 1: Foundation (P3-T01, P3-T02, P3-T03)

```
STEP 1.1: Create AI Module Directory
─────────────────────────────────────
$ mkdir -p api/src/ai
$ touch api/src/ai/__init__.py

STEP 1.2: Define Prompt Contract (P3-T01)
─────────────────────────────────────
File: api/src/ai/prompts.py
Contents:
  - SYSTEM_PROMPT constant (from spec Section 7.1)
  - USER_PROMPT_TEMPLATE with placeholders
  - Helper templates for CLARIFY, ERROR responses

Verification: System prompt contains all AIR rules

STEP 1.3: Define Schemas (P3-T02)
─────────────────────────────────────
File: api/src/ai/schemas.py
Contents:
  - Intent enum (9 values)
  - ActionType enum (2 values)
  - AIAction model
  - AIRequest model
  - AIResponse model
  - AIErrorData model

Verification: All models validate correctly

STEP 1.4: Define TypeScript Types (P3-T02)
─────────────────────────────────────
File: frontend/src/types/ai.ts
Contents:
  - Intent type
  - ActionType type
  - AIAction interface
  - AIRequest interface
  - AIResponse interface
  - ChatMessage interface

Verification: Types match Python schemas

STEP 1.5: Update Environment Configuration (P3-T03)
─────────────────────────────────────
File: api/src/config.py (ADD fields)
File: api/.env.example (ADD variables)
File: api/.env (ADD values - DO NOT COMMIT)

Variables:
  - AI_API_KEY
  - AI_MODEL_NAME
  - AI_TIMEOUT_SECONDS

Verification: Settings load without error
```

### Phase 2: Backend Core (P3-T04, P3-T05, P3-T06)

```
STEP 2.1: Create AI Client (P3-T04)
─────────────────────────────────────
File: api/src/ai/client.py
Contents:
  - AIClient class
  - chat() async method
  - _parse_response() method
  - Error handling for timeouts

Verification: Client can call AI API (mock test)

STEP 2.2: Create AI Route (P3-T04)
─────────────────────────────────────
File: api/src/routes/ai.py
Contents:
  - Router with /chat endpoint
  - get_current_user dependency
  - Request/response handling

File: api/src/routes/__init__.py (UPDATE)
  - Import ai_router
  - Add to api_router

Verification: Endpoint accessible, auth required

STEP 2.3: Create Intent Router (P3-T05)
─────────────────────────────────────
File: api/src/ai/intent_router.py
Contents:
  - IntentRouter class
  - route() method
  - Handler for each intent
  - Validation logic

Verification: Intents route to correct handlers

STEP 2.4: Create Task Executor (P3-T06)
─────────────────────────────────────
File: api/src/ai/task_executor.py
Contents:
  - TaskExecutor class
  - Methods for each operation
  - TaskService integration
  - Message formatting

Verification: Operations execute via TaskService
```

### Phase 3: Backend Security (P3-T07, P3-T12)

```
STEP 3.1: Create Input Sanitizer (P3-T07)
─────────────────────────────────────
File: api/src/ai/sanitizer.py
Contents:
  - InputSanitizer class
  - sanitize() method
  - check_injection_patterns() method
  - escape_output() method

Verification: Injection patterns detected

STEP 3.2: Create Error Handler (P3-T12)
─────────────────────────────────────
File: api/src/ai/errors.py
Contents:
  - Custom exception classes
  - create_error_response() function
  - Error mapping functions

Verification: Errors return AIResponse format

STEP 3.3: Integrate Security into Route
─────────────────────────────────────
File: api/src/routes/ai.py (UPDATE)
  - Add sanitization before processing
  - Add error handling wrapper
  - Add timeout handling

Verification: Security controls active
```

### Phase 4: Frontend Core (P3-T08)

```
STEP 4.1: Create Assistant Components Directory
─────────────────────────────────────
$ mkdir -p frontend/src/components/assistant
$ touch frontend/src/components/assistant/index.ts

STEP 4.2: Create API Client (P3-T08)
─────────────────────────────────────
File: frontend/src/lib/assistant.ts
Contents:
  - sendMessage() function
  - Helper functions

Verification: API calls work

STEP 4.3: Create Chat Components (P3-T08)
─────────────────────────────────────
Files:
  - ChatContainer.tsx
  - MessageList.tsx
  - MessageBubble.tsx
  - ChatInput.tsx

Verification: Chat UI renders correctly

STEP 4.4: Create Assistant Page (P3-T08)
─────────────────────────────────────
File: frontend/src/app/(protected)/assistant/page.tsx
Contents:
  - Import ChatContainer
  - Full-screen layout

File: frontend/src/middleware.ts (UPDATE)
  - Add /assistant to protected paths

Verification: Page accessible when authenticated

STEP 4.5: Add Navigation
─────────────────────────────────────
Add link to /assistant from dashboard header

Verification: Navigation works
```

### Phase 5: Frontend Polish (P3-T09, P3-T10, P3-T11)

```
STEP 5.1: Add Theme Support (P3-T09)
─────────────────────────────────────
Update all chat components with dark/light styles
Add theme toggle to chat header

Verification: Both themes work

STEP 5.2: Add Animations (P3-T10)
─────────────────────────────────────
Files:
  - TypingIndicator.tsx
  - EmptyState.tsx
  - Update MessageBubble.tsx

Add:
  - Message animations
  - Auto-scroll
  - Micro-interactions

Verification: Animations smooth

STEP 5.3: Add Error Handling (P3-T11)
─────────────────────────────────────
File: ErrorMessage.tsx
Update: ChatContainer.tsx

Add:
  - Error display
  - Retry logic
  - Fallback link

Verification: Errors handled gracefully
```

### Phase 6: Testing (P3-T13, P3-T14)

```
STEP 6.1: Write Unit Tests (P3-T13)
─────────────────────────────────────
$ mkdir -p api/tests/unit/test_ai
Create test files per Section 8.2

Run: pytest api/tests/unit/test_ai/ -v
Verification: All tests pass

STEP 6.2: Write Integration Tests (P3-T13)
─────────────────────────────────────
$ mkdir -p api/tests/integration/test_ai
Create test files per Section 8.3

Run: pytest api/tests/integration/test_ai/ -v
Verification: All tests pass

STEP 6.3: Run Regression Tests (P3-T13)
─────────────────────────────────────
Run: pytest backend/tests/ -v  # Phase I
Run: pytest api/tests/ -v      # Phase II (existing)

Verification: No regressions

STEP 6.4: E2E Verification (P3-T14)
─────────────────────────────────────
Execute manual test plan per Section 8.4
Document results in verification-report.md

Verification: All SC criteria pass
```

### Phase 7: Delivery (P3-T15)

```
STEP 7.1: Code Review
─────────────────────────────────────
Review all new files
Check for secrets (none committed)
Verify Phase 2 unchanged

STEP 7.2: Update Documentation
─────────────────────────────────────
Update README.md with:
  - Phase 3 features
  - Environment variables
  - Usage instructions

STEP 7.3: Create Git Tag
─────────────────────────────────────
$ git add .
$ git commit -m "Phase 3: AI Assistant Integration"
$ git tag -a v3.0.0-phase3-ai-assistant -m "Phase 3 complete"

STEP 7.4: Final Verification
─────────────────────────────────────
Run all tests one more time
Verify tag created correctly
Prepare submission
```

---

## 10. File Change Summary

### New Files (16)

| File | Task | Purpose |
|------|------|---------|
| `api/src/ai/__init__.py` | P3-T01 | Module exports |
| `api/src/ai/prompts.py` | P3-T01 | System prompt and templates |
| `api/src/ai/schemas.py` | P3-T02 | AI request/response schemas |
| `api/src/ai/client.py` | P3-T04 | AI model API client |
| `api/src/ai/intent_router.py` | P3-T05 | Intent classification and routing |
| `api/src/ai/task_executor.py` | P3-T06 | Task API integration |
| `api/src/ai/sanitizer.py` | P3-T07 | Input sanitization |
| `api/src/ai/errors.py` | P3-T12 | Error handling |
| `api/src/routes/ai.py` | P3-T04 | AI chat endpoint |
| `frontend/src/types/ai.ts` | P3-T02 | TypeScript types |
| `frontend/src/lib/assistant.ts` | P3-T08 | AI API client |
| `frontend/src/components/assistant/index.ts` | P3-T08 | Component exports |
| `frontend/src/components/assistant/ChatContainer.tsx` | P3-T08 | Chat container |
| `frontend/src/components/assistant/MessageList.tsx` | P3-T08 | Message list |
| `frontend/src/components/assistant/MessageBubble.tsx` | P3-T08 | Message bubble |
| `frontend/src/components/assistant/ChatInput.tsx` | P3-T08 | Chat input |
| `frontend/src/components/assistant/TypingIndicator.tsx` | P3-T10 | Typing indicator |
| `frontend/src/components/assistant/EmptyState.tsx` | P3-T10 | Empty state |
| `frontend/src/components/assistant/ErrorMessage.tsx` | P3-T11 | Error display |
| `frontend/src/app/(protected)/assistant/page.tsx` | P3-T08 | Assistant page |

### Modified Files (4)

| File | Change | Task |
|------|--------|------|
| `api/src/config.py` | Add AI settings fields | P3-T03 |
| `api/src/routes/__init__.py` | Add AI router import | P3-T04 |
| `api/.env.example` | Add AI environment variables | P3-T03 |
| `frontend/src/middleware.ts` | Add /assistant to protected paths | P3-T08 |

### Test Files (New)

| File | Task |
|------|------|
| `api/tests/unit/test_ai/test_schemas.py` | P3-T13 |
| `api/tests/unit/test_ai/test_prompts.py` | P3-T13 |
| `api/tests/unit/test_ai/test_sanitizer.py` | P3-T13 |
| `api/tests/unit/test_ai/test_intent_router.py` | P3-T13 |
| `api/tests/unit/test_ai/test_task_executor.py` | P3-T13 |
| `api/tests/unit/test_ai/test_errors.py` | P3-T13 |
| `api/tests/integration/test_ai/test_ai_endpoint.py` | P3-T13 |

### Unchanged Files

All other files in `api/src/` and `frontend/src/` remain **UNCHANGED** per Phase 2 protection requirements.

---

## Appendix A: Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_API_KEY` | Yes | - | API key for AI model service |
| `AI_MODEL_NAME` | No | `claude-3-haiku-20240307` | AI model identifier |
| `AI_TIMEOUT_SECONDS` | No | `10` | Request timeout |
| `AI_MAX_MESSAGE_LENGTH` | No | `10000` | Max input message length |

---

## Appendix B: API Endpoint Summary

### New Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/ai/chat` | Required | Send message to AI assistant |

### Request/Response

**Request**:
```json
POST /api/v1/ai/chat
Content-Type: application/json
Cookie: auth_token=<jwt>

{
  "message": "Add a task to buy groceries"
}
```

**Response**:
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "intent": "CREATE",
  "message": "I've created a task 'buy groceries' for you.",
  "action": {
    "type": "api_call",
    "endpoint": "/api/v1/tasks",
    "method": "POST",
    "payload": {"title": "buy groceries"}
  },
  "data": {
    "task": {
      "id": "uuid-here",
      "title": "buy groceries",
      "completed": false,
      "created_at": "2026-01-13T..."
    }
  }
}
```
