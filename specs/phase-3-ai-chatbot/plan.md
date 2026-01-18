# Phase III: AI Chatbot Implementation Plan

## Architecture Overview

### Component Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND LAYER                                │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                   Next.js Application                              │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │  │
│  │  │ OpenAI ChatKit  │  │   Auth Context  │  │   Theme Provider    │ │  │
│  │  │  - ChatContainer│  │   - JWT Cookie  │  │   - Dark/Light      │ │  │
│  │  │  - Messages     │  │   - User State  │  │   - System Pref     │ │  │
│  │  │  - Input        │  │                 │  │                     │ │  │
│  │  └────────┬────────┘  └─────────────────┘  └─────────────────────┘ │  │
│  └───────────│────────────────────────────────────────────────────────┘  │
└──────────────│───────────────────────────────────────────────────────────┘
               │ HTTP POST /api/{user_id}/chat
               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                            BACKEND LAYER                                 │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │              FastAPI Application (Stateless)                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │  │
│  │  │   Chat Route    │  │  Conversation   │  │   OpenAI Agents     │ │  │
│  │  │ POST /api/      │──│    Service      │──│      Client         │ │  │
│  │  │ {user_id}/chat  │  │  - Load History │  │  - Agent Runner     │ │  │
│  │  │                 │  │  - Save Messages│  │  - Tool Orchestrator│ │  │
│  │  └─────────────────┘  └────────┬────────┘  └──────────┬──────────┘ │  │
│  └────────────────────────────────│──────────────────────│────────────┘  │
└───────────────────────────────────│──────────────────────│───────────────┘
                                    │                      │
                                    │                      │ MCP Protocol
                                    │                      ▼
┌───────────────────────────────────│──────────────────────────────────────┐
│                            MCP SERVER LAYER                              │
│  ┌────────────────────────────────│────────────────────────────────────┐ │
│  │                   MCP Server (Official SDK)                         │ │
│  │  ┌─────────────────┐  ┌───────▼─────────┐  ┌─────────────────────┐  │ │
│  │  │    add_task     │  │   list_tasks    │  │   complete_task     │  │ │
│  │  │    Tool         │  │     Tool        │  │      Tool           │  │ │
│  │  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │ │
│  │           │                    │                      │             │ │
│  │  ┌────────┴────────┐  ┌────────┴────────┐  ┌──────────┴──────────┐  │ │
│  │  │   delete_task   │  │   update_task   │  │    Task Service     │  │ │
│  │  │      Tool       │  │      Tool       │  │    (DB Access)      │  │ │
│  │  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │ │
│  └───────────│────────────────────│──────────────────────│─────────────┘ │
└──────────────│────────────────────│──────────────────────│───────────────┘
               │                    │                      │
               └────────────────────┼──────────────────────┘
                                    │ SQL Queries
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           DATABASE LAYER                                 │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL (Neon)                               │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │  │
│  │  │     users       │  │     tasks       │  │   conversations     │ │  │
│  │  │  - id (UUID)    │──│  - id (UUID)    │  │  - id (UUID)        │ │  │
│  │  │  - email        │  │  - user_id (FK) │  │  - user_id (FK)     │ │  │
│  │  │  - password_hash│  │  - title        │  │  - created_at       │ │  │
│  │  │  - created_at   │  │  - completed    │  │  - updated_at       │ │  │
│  │  └─────────────────┘  │  - created_at   │  └──────────┬──────────┘ │  │
│  │                       └─────────────────┘             │            │  │
│  │                                          ┌────────────▼──────────┐ │  │
│  │                                          │      messages        │ │  │
│  │                                          │  - id (UUID)         │ │  │
│  │                                          │  - conversation_id   │ │  │
│  │                                          │  - role              │ │  │
│  │                                          │  - content           │ │  │
│  │                                          │  - tool_calls (JSON) │ │  │
│  │                                          │  - tool_results(JSON)│ │  │
│  │                                          │  - created_at        │ │  │
│  │                                          └──────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Implementation Decisions

### Decision 1: MCP Server Implementation

**Options Considered:**
1. In-process MCP tools (same process as FastAPI)
2. Separate MCP Server process (standalone)
3. MCP Server as subprocess spawned by FastAPI

**Decision:** Separate MCP Server process

**Rationale:**
- Clean separation of concerns
- Independent scaling capability
- Follows MCP architecture best practices
- OpenAI Agents SDK connects via stdio transport
- Can be tested independently

**Implementation:**
- Location: `api/src/mcp_server/`
- Entry point: `api/src/mcp_server/server.py`
- Uses `@modelcontextprotocol/sdk` Python package (`mcp`)
- Communicates via stdio with Agent

### Decision 2: OpenAI Agents SDK Integration

**Options Considered:**
1. Direct OpenAI API calls with function calling
2. LangChain with OpenAI
3. OpenAI Agents SDK (`openai-agents`)

**Decision:** OpenAI Agents SDK

**Rationale:**
- Native MCP tool integration
- Built-in conversation management
- Type-safe tool definitions
- Handles streaming and retries
- Production-grade SDK

**Implementation:**
- Location: `api/src/ai/agent.py`
- Model: `gpt-4o` (or configurable)
- Tools: Connected via MCP client

### Decision 3: Conversation Persistence

**Options Considered:**
1. Redis for session storage
2. PostgreSQL with JSONB
3. Dedicated message queue

**Decision:** PostgreSQL with normalized tables

**Rationale:**
- Already using PostgreSQL
- ACID compliance for message ordering
- Supports complex queries (search, filter)
- No additional infrastructure
- Native async support with asyncpg

**Implementation:**
- Tables: `conversations`, `messages`
- Foreign key to `users` with CASCADE delete
- JSONB for tool_calls and tool_results

### Decision 4: Frontend Chat UI

**Options Considered:**
1. Keep custom ChatContainer component
2. OpenAI ChatKit
3. Third-party chat library (Stream Chat, etc.)

**Decision:** OpenAI ChatKit

**Rationale:**
- Official OpenAI component library
- Designed for AI chat interfaces
- Built-in streaming support
- Accessible and responsive
- Consistent with OpenAI products

**Implementation:**
- Replace `ChatContainer.tsx` with ChatKit components
- Maintain dark/light theme support
- Custom styling via Tailwind CSS

## File Structure

```
api/
├── src/
│   ├── ai/                           # AI Module (Updated)
│   │   ├── agent.py                  # OpenAI Agents SDK client
│   │   ├── conversation_service.py   # Conversation history management
│   │   └── schemas.py                # Updated schemas
│   ├── mcp_server/                   # NEW: MCP Server Module
│   │   ├── __init__.py
│   │   ├── server.py                 # MCP Server entry point
│   │   ├── tools.py                  # Tool definitions
│   │   └── task_operations.py        # Database operations for tools
│   ├── db/
│   │   └── migrations/
│   │       └── versions/
│   │           └── 002_conversations.py  # NEW: Migration
│   ├── models/
│   │   ├── conversation.py           # NEW: Conversation model
│   │   └── message.py                # NEW: Message model
│   └── routes/
│       └── chat.py                   # NEW: Chat route handler

frontend/
├── src/
│   ├── app/
│   │   └── (protected)/
│   │       └── assistant/
│   │           └── page.tsx          # Updated to use ChatKit
│   ├── components/
│   │   └── assistant/
│   │       ├── ChatKitWrapper.tsx    # NEW: ChatKit integration
│   │       └── ToolActions.tsx       # NEW: Tool action display
│   └── lib/
│       └── chat.ts                   # Updated API client
```

## Data Flow Sequence

```
┌──────┐     ┌─────────┐     ┌──────────┐     ┌───────┐     ┌────────┐     ┌────┐
│Client│     │ FastAPI │     │  Agent   │     │OpenAI │     │  MCP   │     │ DB │
└──┬───┘     └────┬────┘     └────┬─────┘     └───┬───┘     └───┬────┘     └─┬──┘
   │              │               │               │             │            │
   │ POST /chat   │               │               │             │            │
   │──────────────>               │               │             │            │
   │              │               │               │             │            │
   │              │ Load History  │               │             │            │
   │              │───────────────────────────────────────────────────────────>
   │              │               │               │             │            │
   │              │<──────────────────────────────────────────────────────────│
   │              │  History []   │               │             │            │
   │              │               │               │             │            │
   │              │ Run Agent     │               │             │            │
   │              │───────────────>               │             │            │
   │              │               │               │             │            │
   │              │               │  Chat API     │             │            │
   │              │               │───────────────>             │            │
   │              │               │               │             │            │
   │              │               │   Tool Call   │             │            │
   │              │               │<──────────────│             │            │
   │              │               │               │             │            │
   │              │               │      Call MCP Tool          │            │
   │              │               │─────────────────────────────>            │
   │              │               │               │             │            │
   │              │               │               │             │   SQL      │
   │              │               │               │             │───────────>│
   │              │               │               │             │            │
   │              │               │               │             │<───────────│
   │              │               │               │             │   Result   │
   │              │               │               │             │            │
   │              │               │      Tool Result            │            │
   │              │               │<────────────────────────────│            │
   │              │               │               │             │            │
   │              │               │  Response     │             │            │
   │              │               │───────────────>             │            │
   │              │               │               │             │            │
   │              │               │   Final Msg   │             │            │
   │              │               │<──────────────│             │            │
   │              │               │               │             │            │
   │              │  Agent Result │               │             │            │
   │              │<──────────────│               │             │            │
   │              │               │               │             │            │
   │              │ Save Messages │               │             │            │
   │              │───────────────────────────────────────────────────────────>
   │              │               │               │             │            │
   │   Response   │               │               │             │            │
   │<─────────────│               │               │             │            │
   │              │               │               │             │            │
```

## API Contracts

### POST /api/{user_id}/chat

**Request:**
```typescript
interface ChatRequest {
  message: string;  // 1-10000 characters
}
```

**Response:**
```typescript
interface ChatResponse {
  response: string;           // Natural language response
  actions_taken: Action[];    // Tool calls made
  conversation_id: string;    // UUID for conversation tracking
}

interface Action {
  tool: string;              // Tool name (add_task, list_tasks, etc.)
  result: ToolResult;        // Tool execution result
}

interface ToolResult {
  success: boolean;
  data?: any;                // Task data or list of tasks
  error?: string;            // Error message if failed
}
```

**Error Responses:**
- `400 Bad Request`: Invalid message format
- `401 Unauthorized`: Missing or invalid JWT
- `404 Not Found`: User not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### MCP Tool Schemas

```python
# add_task
{
  "name": "add_task",
  "description": "Create a new task for the user",
  "parameters": {
    "user_id": {"type": "string", "description": "UUID of the user"},
    "title": {"type": "string", "description": "Task title (1-500 chars)"}
  },
  "returns": {
    "success": "boolean",
    "task": {"id": "string", "title": "string", "completed": "boolean"}
  }
}

# list_tasks
{
  "name": "list_tasks",
  "description": "List all tasks for a user with optional filter",
  "parameters": {
    "user_id": {"type": "string", "description": "UUID of the user"},
    "filter": {"type": "string", "enum": ["all", "completed", "incomplete"], "default": "all"}
  },
  "returns": {
    "success": "boolean",
    "tasks": [{"id": "string", "title": "string", "completed": "boolean"}],
    "count": "integer"
  }
}

# complete_task
{
  "name": "complete_task",
  "description": "Mark a task as completed",
  "parameters": {
    "user_id": {"type": "string", "description": "UUID of the user"},
    "task_id": {"type": "string", "description": "UUID of the task"}
  },
  "returns": {
    "success": "boolean",
    "task": {"id": "string", "title": "string", "completed": "boolean"}
  }
}

# delete_task
{
  "name": "delete_task",
  "description": "Delete a task permanently",
  "parameters": {
    "user_id": {"type": "string", "description": "UUID of the user"},
    "task_id": {"type": "string", "description": "UUID of the task"}
  },
  "returns": {
    "success": "boolean",
    "deleted_id": "string",
    "deleted_title": "string"
  }
}

# update_task
{
  "name": "update_task",
  "description": "Update a task's title",
  "parameters": {
    "user_id": {"type": "string", "description": "UUID of the user"},
    "task_id": {"type": "string", "description": "UUID of the task"},
    "title": {"type": "string", "description": "New task title (1-500 chars)"}
  },
  "returns": {
    "success": "boolean",
    "task": {"id": "string", "title": "string", "completed": "boolean"}
  }
}
```

## Environment Configuration

### Backend (.env additions)
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=1024
OPENAI_TEMPERATURE=0.7

# MCP Server Configuration
MCP_SERVER_PATH=api/src/mcp_server/server.py
MCP_TRANSPORT=stdio
```

## Security Considerations

1. **User Isolation**: MCP tools always receive user_id from authenticated context, never from AI
2. **Input Validation**: All tool parameters validated before execution
3. **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
4. **Rate Limiting**: 30 requests/minute per user on chat endpoint
5. **Error Sanitization**: No internal details in error responses

## Testing Strategy

1. **Unit Tests**: MCP tools, conversation service
2. **Integration Tests**: Chat endpoint with mocked OpenAI
3. **E2E Tests**: Full flow from frontend to database
4. **Load Tests**: Verify rate limiting and performance

## Rollback Plan

1. Keep existing `/api/v1/ai/chat` endpoint functional
2. New endpoint at `/api/{user_id}/chat`
3. Frontend feature flag to switch between implementations
4. Database migration is additive (no destructive changes)

## Dependencies to Install

### Backend
```
openai>=1.0.0
openai-agents>=0.1.0
mcp>=1.0.0
```

### Frontend
```
@openai/chatkit
```
