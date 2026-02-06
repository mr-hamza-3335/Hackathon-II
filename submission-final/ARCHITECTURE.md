# PakAura System Architecture

## High-Level Overview

PakAura is a full-stack, AI-powered task management application built with a modern microservices-ready architecture. The system comprises three main layers: a Next.js frontend, a FastAPI backend, and a PostgreSQL database, with Cohere AI integration for natural language processing.

## System Diagram

```
+-------------------------------------------------------------------+
|                      Client (Browser)                              |
|  +--------------------------------------------------------------+ |
|  |              Next.js 14 Frontend (Port 3000)                  | |
|  |                                                               | |
|  |  +------------+  +------------+  +-------------------------+  | |
|  |  | Auth Pages |  | Dashboard  |  |    AI Assistant          |  | |
|  |  | Login/Reg  |  | Task CRUD  |  |    Chat Interface        |  | |
|  |  +------------+  +------------+  +-------------------------+  | |
|  |                                                               | |
|  |  +----------------------------------------------------------+ | |
|  |  |       API Client (fetch + credentials: include)           | | |
|  |  +----------------------------------------------------------+ | |
|  +--------------------------------------------------------------+ |
+-------------------------------------------------------------------+
                          | HTTP (JWT in cookies)
                          v
+-------------------------------------------------------------------+
|                 FastAPI Backend (Port 8000)                         |
|                                                                    |
|  +--------------------------------------------------------------+ |
|  |          Middleware: CORS | Rate Limiting | JWT Auth           | |
|  +--------------------------------------------------------------+ |
|                                                                    |
|  +-----------+ +----------+ +---------+ +----------------------+ |
|  | Auth API  | | Task API | | AI API  | | Chat API             | |
|  | /auth/*   | | /tasks/* | | /ai/*   | | /{user_id}/chat      | |
|  +-----------+ +----------+ +---------+ +----------------------+ |
|                                                                    |
|  +-----------+ +----------+ +----------------------------------+ |
|  | Auth      | | Task     | | AI Layer                         | |
|  | Service   | | Service  | |  +-------------+ +-------------+ | |
|  | (bcrypt)  | | (CRUD)   | |  | Cohere Agent| | MCP Tools   | | |
|  | (JWT)     | |          | |  | Intent Det. | | Task Ops    | | |
|  +-----------+ +----------+ |  +-------------+ +-------------+ | |
|                              +----------------------------------+ |
|                                                                    |
|  +--------------------------------------------------------------+ |
|  |         SQLAlchemy ORM (async) + asyncpg driver               | |
|  +--------------------------------------------------------------+ |
+-------------------------------------------------------------------+
                          |
                          v
+-------------------------------------------------------------------+
|                    PostgreSQL 16                                    |
|                                                                    |
|  +--------+  +--------+  +--------------+  +----------+          |
|  | users  |  | tasks  |  |conversations |  | messages |          |
|  +--------+  +--------+  +--------------+  +----------+          |
+-------------------------------------------------------------------+

External:
+-------------------------------------------------------------------+
|                    Cohere AI API (FREE Tier)                        |
|                    Model: command-a-03-2025                         |
+-------------------------------------------------------------------+
```

## Component Details

### Frontend (Next.js 14)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Next.js 14 (App Router) | Server/client rendering |
| Language | TypeScript 5.3 | Type safety |
| Styling | Tailwind CSS 3.4 | Utility-first CSS |
| Animations | Framer Motion 12 | Smooth UI transitions |
| Icons | Lucide React | Consistent iconography |
| Theming | next-themes | Dark/light mode |

**Route Structure:**
```
app/
  page.tsx              -> / (redirect to login/dashboard)
  (auth)/
    login/page.tsx      -> /login
    register/page.tsx   -> /register
  (protected)/
    layout.tsx          -> Auth guard + navigation
    dashboard/page.tsx  -> /dashboard (task management)
    assistant/page.tsx  -> /assistant (AI chat)
```

### Backend (FastAPI)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | FastAPI 0.109+ | Async REST API |
| ORM | SQLAlchemy 2.0 (async) | Database abstraction |
| Driver | asyncpg 0.29+ | PostgreSQL async driver |
| Auth | python-jose + bcrypt | JWT tokens + password hashing |
| AI | Cohere API (httpx) | Natural language processing |
| Validation | Pydantic 2.12+ | Request/response validation |

### Database Schema

```
users
+------------+------------------+------------------+
| Column     | Type             | Constraints      |
+------------+------------------+------------------+
| id         | UUID (PK)        | auto-generated   |
| email      | VARCHAR (unique) | case-insensitive |
| pass_hash  | VARCHAR          | bcrypt(12)       |
| created_at | TIMESTAMP        | auto             |
| updated_at | TIMESTAMP        | auto             |
+------------+------------------+------------------+

tasks
+------------+------------------+------------------+
| Column     | Type             | Constraints      |
+------------+------------------+------------------+
| id         | UUID (PK)        | auto-generated   |
| user_id    | UUID (FK->users) | NOT NULL         |
| title      | VARCHAR(500)     | 1-500 chars      |
| completed  | BOOLEAN          | default: false   |
| created_at | TIMESTAMP        | auto             |
| updated_at | TIMESTAMP        | auto             |
+------------+------------------+------------------+

conversations
+------------+------------------+------------------+
| Column     | Type             | Constraints      |
+------------+------------------+------------------+
| id         | UUID (PK)        | auto-generated   |
| user_id    | UUID (FK->users) | NOT NULL         |
| created_at | TIMESTAMP        | auto             |
| updated_at | TIMESTAMP        | auto             |
+------------+------------------+------------------+

messages
+-----------------+------------------+---------------------+
| Column          | Type             | Constraints         |
+-----------------+------------------+---------------------+
| id              | UUID (PK)        | auto-generated      |
| conversation_id | UUID (FK)        | NOT NULL            |
| role            | VARCHAR          | user/assistant      |
| content         | TEXT             | message content     |
| tool_calls      | JSON (nullable)  | tool call data      |
| created_at      | TIMESTAMP        | auto                |
+-----------------+------------------+---------------------+
```

## Authentication Flow

```
Registration/Login:
  Browser                    Backend                   Database
    |                          |                          |
    |-- POST /auth/login ----->|                          |
    |   {email, password}      |-- SELECT user by email ->|
    |                          |<-- user record ----------|
    |                          |                          |
    |                          |-- verify bcrypt hash     |
    |                          |-- generate JWT (HS256)   |
    |                          |                          |
    |<-- 200 + Set-Cookie ----|                          |
    |   auth_token=<jwt>       |                          |
    |   HttpOnly, SameSite=Lax |                          |
    |                          |                          |

Protected Request:
  Browser                    Backend                   Database
    |                          |                          |
    |-- GET /tasks ----------->|                          |
    |   Cookie: auth_token=jwt |                          |
    |                          |-- decode JWT             |
    |                          |-- extract user_id        |
    |                          |-- SELECT user by id ---->|
    |                          |<-- user record ----------|
    |                          |-- SELECT tasks by uid -->|
    |                          |<-- task list ------------|
    |<-- 200 {tasks} ---------|                          |
    |                          |                          |

Logout:
  Browser                    Backend
    |                          |
    |-- POST /auth/logout ---->|
    |                          |-- delete cookie
    |<-- 200 + Clear-Cookie --|
    |                          |
```

## AI Chat Processing Flow

```
User Message -> Intent Detection -> Execution -> Response

Detailed Flow:
  1. User sends: "add task buy groceries"
  2. ChatKitWrapper -> POST /api/{user_id}/chat
  3. Backend verifies JWT auth
  4. Input sanitization (control chars, length)
  5. Agent.initialize() -> TaskOperations(db_url)
  6. Agent._detect_intent("add task buy groceries")
     -> Returns: ("add_task", {"title": "buy groceries"})
  7. Agent calls self.task_ops.add_task(user_id, "buy groceries")
     -> Inserts into PostgreSQL
     -> Returns: {"success": true, "task": {...}}
  8. If Cohere API configured:
     -> Enhance response with AI-generated text
  9. Return AgentResult(response="...", tool_calls=[...])
  10. Save messages to conversation history
  11. Return ChatResponse to frontend
  12. Frontend displays response + tool actions

Supported Intents:
  +-------------------+----------------------------------+
  | Intent            | Example Commands                 |
  +-------------------+----------------------------------+
  | greeting          | "hello", "hi", "hey"             |
  | help              | "help", "what can you do"        |
  | add_task          | "add task buy milk"              |
  | list_tasks        | "show all my tasks"              |
  | complete_task     | "complete buy milk"              |
  | uncomplete_task   | "uncomplete buy milk"            |
  | delete_task       | "delete buy milk"                |
  | clear_completed   | "clear completed tasks"          |
  | update_task       | "update buy milk to buy cheese"  |
  | unknown           | General conversation -> Cohere   |
  +-------------------+----------------------------------+
```

## Kubernetes Deployment

```
Namespace: pakaura
+-------------------------------------------------------------------+
|                                                                    |
|  +-------------------+  +------------------+ +------------------+ |
|  | Deployment:       |  | Deployment:      | | Deployment:      | |
|  | frontend (1 rep)  |  | api (1 rep)      | | postgres (1 rep) | |
|  |                   |  |                  | |                  | |
|  | Next.js           |  | FastAPI          | | PostgreSQL 16    | |
|  | Port: 3000        |  | Port: 8000       | | Port: 5432       | |
|  +-------------------+  +------------------+ +------------------+ |
|         |                        |                    |            |
|  +-------------------+  +------------------+ +------------------+ |
|  | Service:          |  | Service:         | | Service:         | |
|  | NodePort 30300    |  | NodePort 30800   | | ClusterIP        | |
|  +-------------------+  +------------------+ +------------------+ |
|                                                                    |
|  +--------------------------------------------------------------+ |
|  | Secret: pakaura-secrets                                       | |
|  |   DATABASE_URL, JWT_SECRET, COHERE_API_KEY                    | |
|  +--------------------------------------------------------------+ |
|  +--------------------------------------------------------------+ |
|  | ConfigMap: pakaura-config                                     | |
|  |   ENVIRONMENT, FRONTEND_URL, AI_MODEL, etc.                   | |
|  +--------------------------------------------------------------+ |
+-------------------------------------------------------------------+
```

## Security Architecture

| Layer | Mechanism | Details |
|-------|-----------|---------|
| Transport | HTTPS (production) | TLS termination at ingress |
| Authentication | JWT (HS256) | 24-hour expiration |
| Token Storage | HTTP-only cookies | Prevents XSS access |
| CSRF | SameSite=Lax | Browser-enforced |
| Authorization | User isolation | All queries filter by user_id |
| Input | Sanitization | Control chars removed, length limits |
| Rate Limiting | Sliding window | 10/min auth, 100/min tasks |
| CORS | Origin whitelist | Only frontend origin allowed |
| Passwords | bcrypt (cost 12) | Industry standard hashing |
| Secrets | Environment vars | Never in code, K8s Secrets in prod |
| Error Messages | Generic | No information leakage |

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AI Provider | Cohere (FREE tier) | Zero cost, good NLU, easy API |
| Frontend | Next.js 14 | App Router, SSR/SSG, TypeScript |
| Backend | FastAPI | Async, auto-docs, Pydantic |
| Database | PostgreSQL | Reliable, JSON support, async |
| Auth | JWT + Cookies | Stateless, XSS-safe |
| Deployment | Helm + K8s | Production-grade, portable |
| Styling | Tailwind CSS | Rapid development, consistent |
| Animation | Framer Motion | Smooth, declarative |
