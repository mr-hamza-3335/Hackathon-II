# Phase III: AI Chatbot with OpenAI Agents SDK & MCP Server

## Feature Overview

**Feature Name**: AI-Powered Task Management Chatbot
**Version**: 3.0.0
**Status**: In Development
**Created**: 2026-01-15
**Branch**: `001-ai-assistant-integration`

## Problem Statement

Users need a natural language interface to manage their tasks conversationally. The current implementation uses Cohere API with custom intent logic, which lacks:
- Proper tool-calling capabilities via standardized protocols
- Persistent conversation history across sessions
- Stateless, scalable architecture
- Industry-standard AI SDK integration

## Solution Overview

Implement a conversational AI chatbot using:
1. **OpenAI Agents SDK** - For agent orchestration and tool calling
2. **Official MCP SDK** - Model Context Protocol server exposing task management tools
3. **PostgreSQL** - Persistent storage for conversation history and task state
4. **OpenAI ChatKit** - Modern, pre-built frontend chat UI components

## Functional Requirements

### FR-1: MCP Server (Model Context Protocol)

The MCP Server MUST:
- Be implemented as a separate, standalone server using the **Official MCP SDK** (`@modelcontextprotocol/sdk`)
- Expose exactly 5 tools via MCP protocol:

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `add_task` | Create a new task | `user_id: string`, `title: string` |
| `list_tasks` | List user's tasks | `user_id: string`, `filter?: 'all' \| 'completed' \| 'incomplete'` |
| `complete_task` | Mark task as done | `user_id: string`, `task_id: string` |
| `delete_task` | Remove a task | `user_id: string`, `task_id: string` |
| `update_task` | Update task title | `user_id: string`, `task_id: string`, `title: string` |

- Be **stateless** - no in-memory state, all persistence via PostgreSQL
- Use the same PostgreSQL database as the main backend
- Return structured JSON responses with success/error status
- Handle `task_not_found` errors gracefully with user-friendly messages

### FR-2: OpenAI Agents SDK Integration

The AI Agent MUST:
- Use **OpenAI Agents SDK** (`openai-agents`) for agent orchestration
- Connect to MCP Server tools (NOT direct database access)
- Maintain conversation context via database-backed history
- Be conversational, friendly, and explanatory in responses
- Confirm all actions in natural language before execution
- Handle errors gracefully with helpful suggestions

### FR-3: Chat API Endpoint

Implement `POST /api/{user_id}/chat`:

**Request:**
```json
{
  "message": "string (user's natural language input)"
}
```

**Response:**
```json
{
  "response": "string (AI's natural language response)",
  "actions_taken": [
    {
      "tool": "string (tool name)",
      "result": "object (tool result)"
    }
  ]
}
```

**Requirements:**
- User ID from URL path (authenticated via JWT)
- Conversation history loaded from database per request
- New messages appended to conversation history
- FastAPI backend MUST remain stateless
- Rate limiting: 30 requests per minute per user

### FR-4: Conversation History Persistence

**Database Schema:**
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  tool_calls JSONB,
  tool_results JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Requirements:**
- Conversations persist across server restarts
- History automatically loaded when chat endpoint called
- Supports conversation resumption
- Messages include tool call/result metadata

### FR-5: Frontend with OpenAI ChatKit

Replace current custom chat UI with **OpenAI ChatKit** components:
- Use official ChatKit package for chat interface
- Maintain responsive design (mobile-first)
- Support dark/light theme
- Show loading states during AI processing
- Display tool actions taken (expandable)
- Quick action buttons for common commands

## Non-Functional Requirements

### NFR-1: Performance
- Chat response latency: < 5 seconds p95
- MCP tool execution: < 500ms p95
- Database queries: < 100ms p95

### NFR-2: Reliability
- Graceful degradation if OpenAI API unavailable
- Retry logic for transient failures (3 attempts)
- Circuit breaker for repeated failures

### NFR-3: Security
- JWT authentication required for all chat endpoints
- User can only access their own tasks via MCP tools
- Input sanitization for all user messages
- No sensitive data in logs or error messages

### NFR-4: Scalability
- Stateless design allows horizontal scaling
- MCP Server can be scaled independently
- Connection pooling for database

## Technical Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js       │     │   FastAPI       │     │   MCP Server    │
│   Frontend      │────>│   Backend       │────>│   (MCP SDK)     │
│   (ChatKit)     │     │   (Stateless)   │     │                 │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                                 │                       │
                                 │  OpenAI Agents SDK    │
                                 │  (Tool Calling)       │
                                 │                       │
                        ┌────────▼────────┐              │
                        │   OpenAI API    │              │
                        │   (GPT-4)       │              │
                        └─────────────────┘              │
                                                         │
                        ┌────────────────────────────────▼─┐
                        │         PostgreSQL               │
                        │  ┌───────────┬───────────────┐   │
                        │  │   users   │ conversations │   │
                        │  │   tasks   │   messages    │   │
                        │  └───────────┴───────────────┘   │
                        └──────────────────────────────────┘
```

## Data Flow

1. User sends message via ChatKit UI
2. Frontend POSTs to `/api/{user_id}/chat`
3. FastAPI loads conversation history from PostgreSQL
4. OpenAI Agents SDK processes message with history context
5. Agent determines required tool calls
6. Agent calls MCP Server tools as needed
7. MCP tools execute against PostgreSQL
8. Agent formulates natural language response
9. New messages saved to PostgreSQL
10. Response returned to frontend
11. ChatKit displays response with tool actions

## Example Interactions

### Example 1: Create Task
```
User: "Add a task to buy groceries"
Assistant: "I've created a new task 'buy groceries' for you. Is there anything else you'd like me to help with?"
Actions: [{ tool: "add_task", result: { id: "...", title: "buy groceries", completed: false } }]
```

### Example 2: List Tasks
```
User: "What's on my list?"
Assistant: "You have 3 tasks:
1. Buy groceries (pending)
2. Call mom (pending)
3. Review PR (completed)

Would you like me to help you with any of these?"
Actions: [{ tool: "list_tasks", result: { tasks: [...], count: 3 } }]
```

### Example 3: Complete Task
```
User: "I finished buying groceries"
Assistant: "Great job! I've marked 'buy groceries' as complete. You've completed 2 out of 3 tasks today!"
Actions: [{ tool: "complete_task", result: { id: "...", title: "buy groceries", completed: true } }]
```

### Example 4: Delete Task
```
User: "Remove the grocery task"
Assistant: "I've deleted the task 'buy groceries'. Your list now has 2 remaining tasks."
Actions: [{ tool: "delete_task", result: { deleted: true, title: "buy groceries" } }]
```

### Example 5: Task Not Found
```
User: "Complete my workout task"
Assistant: "I couldn't find a task about 'workout' in your list. Here are your current tasks:
1. Call mom (pending)
2. Review PR (completed)

Would you like me to create a workout task for you instead?"
Actions: [{ tool: "list_tasks", result: { tasks: [...] } }]
```

## Acceptance Criteria

- [ ] MCP Server implemented with Official MCP SDK
- [ ] MCP Server exposes 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
- [ ] MCP tools are stateless (all state in PostgreSQL)
- [ ] OpenAI Agents SDK integrated for agent orchestration
- [ ] Agent calls MCP tools (not direct DB access)
- [ ] POST /api/{user_id}/chat endpoint implemented
- [ ] Conversation history stored in PostgreSQL
- [ ] Conversations resume after server restart
- [ ] Frontend uses OpenAI ChatKit components
- [ ] Agent responses are conversational and friendly
- [ ] Agent confirms actions in natural language
- [ ] Task-not-found errors handled gracefully
- [ ] All existing tests pass
- [ ] New integration tests for chat flow

## Dependencies

### Backend
- `openai-agents` - OpenAI Agents SDK (Python)
- `mcp` - Official MCP SDK (Python)
- `openai` - OpenAI Python client
- Existing: FastAPI, SQLAlchemy, asyncpg, PostgreSQL

### Frontend
- `@openai/chatkit` - OpenAI ChatKit components
- Existing: Next.js, React, Framer Motion, Tailwind CSS

## Out of Scope

- Voice input/output
- Multi-user collaboration
- Task scheduling/reminders
- File attachments
- Offline mode
- Mobile native apps

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API rate limits | Service degradation | Implement retry logic, cache responses |
| MCP SDK compatibility | Integration issues | Use official SDK, test thoroughly |
| Conversation history growth | Storage costs | Implement history pruning policy |
| ChatKit customization limits | UX constraints | Evaluate alternatives, custom CSS |

## Success Metrics

- Chat response success rate: > 99%
- Average response time: < 3 seconds
- User satisfaction (task completion rate): > 95%
- Error rate: < 1%
