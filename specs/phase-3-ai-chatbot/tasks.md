# Phase III: AI Chatbot Implementation Tasks

## Task Overview

| ID | Task | Status | Priority | Dependencies |
|----|------|--------|----------|--------------|
| T1 | Database Migration | Pending | High | None |
| T2 | MCP Server Implementation | Pending | High | T1 |
| T3 | OpenAI Agents Integration | Pending | High | T2 |
| T4 | Chat API Endpoint | Pending | High | T3 |
| T5 | Frontend ChatKit Integration | Pending | Medium | T4 |
| T6 | End-to-End Testing | Pending | Medium | T5 |

---

## T1: Database Migration for Conversation History

### Description
Create Alembic migration to add `conversations` and `messages` tables for persistent chat history.

### Files to Create/Modify
- [ ] `api/src/db/migrations/versions/002_conversations.py` (NEW)
- [ ] `api/src/models/conversation.py` (NEW)
- [ ] `api/src/models/message.py` (NEW)
- [ ] `api/src/models/__init__.py` (UPDATE)

### Implementation Details

#### 002_conversations.py
```python
"""Add conversations and messages tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # conversations table
    op.create_table(
        'conversations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('tool_calls', JSONB, nullable=True),
        sa.Column('tool_results', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='valid_role')
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['conversation_id', 'created_at'])

def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
```

### Acceptance Criteria
- [ ] Migration runs successfully with `alembic upgrade head`
- [ ] Tables created with correct schema
- [ ] Foreign keys enforce user isolation
- [ ] Indexes created for performance

---

## T2: MCP Server Implementation

### Description
Implement standalone MCP Server using Official MCP SDK with 5 task management tools.

### Files to Create
- [ ] `api/src/mcp_server/__init__.py` (NEW)
- [ ] `api/src/mcp_server/server.py` (NEW)
- [ ] `api/src/mcp_server/tools.py` (NEW)
- [ ] `api/src/mcp_server/task_operations.py` (NEW)

### Implementation Details

#### server.py
```python
"""MCP Server for Task Management

Exposes tools: add_task, list_tasks, complete_task, delete_task, update_task
All tools are stateless - state persisted in PostgreSQL
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from .tools import register_tools

async def main():
    server = Server("task-manager")
    register_tools(server)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
```

#### tools.py
```python
"""MCP Tool Definitions"""
from mcp.server import Server
from mcp.types import Tool, TextContent
from .task_operations import TaskOperations

def register_tools(server: Server):
    ops = TaskOperations()

    @server.list_tools()
    async def list_tools():
        return [
            Tool(name="add_task", description="Create a new task", inputSchema={...}),
            Tool(name="list_tasks", description="List user's tasks", inputSchema={...}),
            Tool(name="complete_task", description="Mark task as done", inputSchema={...}),
            Tool(name="delete_task", description="Delete a task", inputSchema={...}),
            Tool(name="update_task", description="Update task title", inputSchema={...}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "add_task":
            result = await ops.add_task(arguments["user_id"], arguments["title"])
        elif name == "list_tasks":
            result = await ops.list_tasks(arguments["user_id"], arguments.get("filter", "all"))
        # ... other tools
        return [TextContent(type="text", text=json.dumps(result))]
```

#### task_operations.py
```python
"""Database operations for MCP tools - stateless, all state in PostgreSQL"""
import asyncpg
from uuid import UUID

class TaskOperations:
    async def get_connection(self):
        return await asyncpg.connect(DATABASE_URL)

    async def add_task(self, user_id: str, title: str) -> dict:
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow(
                "INSERT INTO tasks (user_id, title) VALUES ($1, $2) RETURNING id, title, completed",
                UUID(user_id), title
            )
            return {"success": True, "task": dict(row)}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await conn.close()

    async def list_tasks(self, user_id: str, filter: str = "all") -> dict:
        # ... implementation

    async def complete_task(self, user_id: str, task_id: str) -> dict:
        # ... implementation

    async def delete_task(self, user_id: str, task_id: str) -> dict:
        # ... implementation

    async def update_task(self, user_id: str, task_id: str, title: str) -> dict:
        # ... implementation
```

### Acceptance Criteria
- [ ] MCP Server starts without errors
- [ ] All 5 tools registered and callable
- [ ] Tools are stateless (no in-memory state)
- [ ] Database operations work correctly
- [ ] Error handling returns user-friendly messages
- [ ] task_not_found handled gracefully

---

## T3: OpenAI Agents SDK Integration

### Description
Integrate OpenAI Agents SDK to orchestrate the AI agent with MCP tools.

### Files to Create/Modify
- [ ] `api/src/ai/agent.py` (NEW)
- [ ] `api/src/ai/conversation_service.py` (NEW)
- [ ] `api/src/config.py` (UPDATE)
- [ ] `api/requirements.txt` (UPDATE)

### Implementation Details

#### agent.py
```python
"""OpenAI Agents SDK Integration"""
from openai_agents import Agent, AgentRunner
from openai_agents.mcp import MCPClient
import subprocess

class TaskManagerAgent:
    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.mcp_process = None
        self.agent = None

    async def initialize(self):
        # Start MCP Server as subprocess
        self.mcp_process = subprocess.Popen(
            ["python", "-m", "api.src.mcp_server.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Connect MCP client
        mcp_client = MCPClient(stdio=(self.mcp_process.stdin, self.mcp_process.stdout))
        await mcp_client.connect()

        # Create agent with MCP tools
        self.agent = Agent(
            name="TaskManager",
            model="gpt-4o",
            instructions=SYSTEM_PROMPT,
            tools=await mcp_client.get_tools()
        )

    async def chat(self, user_id: str, message: str, history: list) -> dict:
        """Process user message with conversation history"""
        runner = AgentRunner(self.agent)

        # Inject user_id into tool calls
        result = await runner.run(
            messages=history + [{"role": "user", "content": message}],
            context={"user_id": user_id}
        )

        return {
            "response": result.final_message,
            "actions_taken": result.tool_calls
        }

    async def cleanup(self):
        if self.mcp_process:
            self.mcp_process.terminate()
```

#### conversation_service.py
```python
"""Conversation History Management"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.conversation import Conversation
from models.message import Message

class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_conversation(self, user_id: str) -> Conversation:
        """Get existing conversation or create new one"""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            conversation = Conversation(user_id=user_id)
            self.db.add(conversation)
            await self.db.commit()

        return conversation

    async def get_history(self, conversation_id: str) -> list:
        """Load conversation history from database"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()

        return [
            {
                "role": m.role,
                "content": m.content,
                "tool_calls": m.tool_calls,
                "tool_results": m.tool_results
            }
            for m in messages
        ]

    async def save_message(self, conversation_id: str, role: str, content: str,
                          tool_calls: dict = None, tool_results: dict = None):
        """Save message to database"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_results=tool_results
        )
        self.db.add(message)
        await self.db.commit()
```

### Acceptance Criteria
- [ ] OpenAI Agents SDK initializes correctly
- [ ] MCP Server spawned as subprocess
- [ ] Agent connects to MCP tools
- [ ] Conversation history loaded from database
- [ ] New messages saved to database
- [ ] Tool calls executed through MCP

---

## T4: Chat API Endpoint

### Description
Implement `POST /api/{user_id}/chat` endpoint with stateless request handling.

### Files to Create/Modify
- [ ] `api/src/routes/chat.py` (NEW)
- [ ] `api/src/main.py` (UPDATE)

### Implementation Details

#### chat.py
```python
"""Chat API Route Handler"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from middleware.auth import get_current_user
from ai.agent import TaskManagerAgent
from ai.conversation_service import ConversationService
from db.connection import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)

class ActionTaken(BaseModel):
    tool: str
    result: dict

class ChatResponse(BaseModel):
    response: str
    actions_taken: list[ActionTaken]
    conversation_id: str

@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    # Verify user_id matches authenticated user
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Initialize services
    conversation_service = ConversationService(db)
    agent = TaskManagerAgent(settings.OPENAI_API_KEY)

    try:
        await agent.initialize()

        # Get or create conversation
        conversation = await conversation_service.get_or_create_conversation(user_id)

        # Load conversation history
        history = await conversation_service.get_history(str(conversation.id))

        # Process message with agent
        result = await agent.chat(user_id, request.message, history)

        # Save user message
        await conversation_service.save_message(
            str(conversation.id), "user", request.message
        )

        # Save assistant response
        await conversation_service.save_message(
            str(conversation.id), "assistant", result["response"],
            tool_calls=result.get("actions_taken")
        )

        return ChatResponse(
            response=result["response"],
            actions_taken=[
                ActionTaken(tool=a["tool"], result=a["result"])
                for a in result.get("actions_taken", [])
            ],
            conversation_id=str(conversation.id)
        )

    finally:
        await agent.cleanup()
```

### Acceptance Criteria
- [ ] Endpoint accessible at `/api/{user_id}/chat`
- [ ] JWT authentication required
- [ ] User can only access their own chat
- [ ] Conversation history loaded per request
- [ ] Messages saved after processing
- [ ] Rate limiting enforced (30/min)

---

## T5: Frontend ChatKit Integration

### Description
Replace custom chat UI with OpenAI ChatKit components.

### Files to Create/Modify
- [ ] `frontend/src/components/assistant/ChatKitWrapper.tsx` (NEW)
- [ ] `frontend/src/components/assistant/ToolActions.tsx` (NEW)
- [ ] `frontend/src/app/(protected)/assistant/page.tsx` (UPDATE)
- [ ] `frontend/src/lib/chat.ts` (UPDATE)
- [ ] `frontend/package.json` (UPDATE)

### Implementation Details

#### ChatKitWrapper.tsx
```tsx
"use client";

import { Chat, ChatInput, ChatMessages } from "@openai/chatkit";
import { useState } from "react";
import { sendChatMessage } from "@/lib/chat";
import { ToolActions } from "./ToolActions";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  actions?: { tool: string; result: any }[];
}

export function ChatKitWrapper({ userId }: { userId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(userId, content);

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.response,
        actions: response.actions_taken,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      // Handle error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Chat>
      <ChatMessages>
        {messages.map((msg) => (
          <div key={msg.id}>
            <ChatMessage role={msg.role} content={msg.content} />
            {msg.actions && <ToolActions actions={msg.actions} />}
          </div>
        ))}
      </ChatMessages>
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </Chat>
  );
}
```

#### ToolActions.tsx
```tsx
"use client";

import { ChevronDown, ChevronUp, Wrench } from "lucide-react";
import { useState } from "react";

interface Action {
  tool: string;
  result: any;
}

export function ToolActions({ actions }: { actions: Action[] }) {
  const [expanded, setExpanded] = useState(false);

  if (!actions || actions.length === 0) return null;

  return (
    <div className="mt-2 border-l-2 border-emerald-500 pl-3">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm text-gray-500"
      >
        <Wrench className="h-4 w-4" />
        {actions.length} action{actions.length > 1 ? "s" : ""} taken
        {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {expanded && (
        <ul className="mt-2 space-y-1">
          {actions.map((action, idx) => (
            <li key={idx} className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded">
              <span className="font-mono">{action.tool}</span>
              <pre className="mt-1 overflow-auto">
                {JSON.stringify(action.result, null, 2)}
              </pre>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Acceptance Criteria
- [ ] ChatKit components render correctly
- [ ] Messages display with proper styling
- [ ] Tool actions expandable/collapsible
- [ ] Dark/light theme supported
- [ ] Responsive design maintained
- [ ] Loading states shown during API calls

---

## T6: End-to-End Testing

### Description
Verify complete flow from frontend to database with example commands.

### Test Scenarios

| # | User Input | Expected Behavior |
|---|------------|-------------------|
| 1 | "Add a task to buy groceries" | Task created, confirmation shown |
| 2 | "Show my tasks" | Task list displayed |
| 3 | "Mark buy groceries as done" | Task completed, confirmation shown |
| 4 | "Change buy groceries to buy organic groceries" | Task updated, confirmation shown |
| 5 | "Delete the grocery task" | Task deleted, confirmation shown |
| 6 | "Complete my workout task" | Error handled: task not found |
| 7 | Server restart, then "Show my tasks" | Conversation resumes correctly |

### Test Commands
```bash
# 1. Start backend
cd api && uvicorn src.main:app --reload

# 2. Start frontend
cd frontend && npm run dev

# 3. Run integration tests
cd api && pytest tests/integration/test_chat.py -v

# 4. Manual testing checklist
- [ ] Create task via chat
- [ ] List tasks via chat
- [ ] Complete task via chat
- [ ] Update task via chat
- [ ] Delete task via chat
- [ ] Handle task not found
- [ ] Restart server, verify conversation resumes
```

### Acceptance Criteria
- [ ] All 7 test scenarios pass
- [ ] Conversation history persists across restarts
- [ ] Error messages are user-friendly
- [ ] Agent responses are conversational
- [ ] Tool actions visible in UI

---

## Dependency Order

```
T1 (Database Migration)
    │
    ▼
T2 (MCP Server)
    │
    ▼
T3 (OpenAI Agents)
    │
    ▼
T4 (Chat Endpoint)
    │
    ▼
T5 (Frontend ChatKit)
    │
    ▼
T6 (E2E Testing)
```

## Estimated Complexity

| Task | Files | Lines of Code |
|------|-------|---------------|
| T1 | 4 | ~150 |
| T2 | 4 | ~300 |
| T3 | 3 | ~250 |
| T4 | 2 | ~150 |
| T5 | 4 | ~300 |
| T6 | 2 | ~100 |
| **Total** | **19** | **~1250** |
