# PakAura -- AI-Powered Task Management

**PakAura** is a full-stack, cloud-native task management platform that combines traditional CRUD operations with an intelligent AI chatbot. Users manage tasks through a sleek web interface or by conversing with an AI assistant powered by Cohere's free-tier language model. The system is built for production readiness with JWT authentication, async database operations, rate limiting, and Kubernetes deployment via Helm charts.

---

## Table of Contents

1. [Features](#features)
2. [Architecture Overview](#architecture-overview)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Quick Start](#quick-start)
   - [Prerequisites](#prerequisites)
   - [Local Development](#local-development)
   - [Docker Compose](#docker-compose)
   - [Kubernetes (Minikube)](#kubernetes-minikube)
6. [Environment Variables](#environment-variables)
7. [API Documentation](#api-documentation)
8. [AI Chatbot Guide](#ai-chatbot-guide)
9. [Deployment Guide](#deployment-guide)
10. [Screenshots](#screenshots)
11. [Testing](#testing)
12. [Contributing](#contributing)
13. [License](#license)

---

## Features

| Category | Capability |
|---|---|
| **Authentication** | User registration and login with JWT tokens stored in HTTP-only cookies; 24-hour token expiration; bcrypt password hashing |
| **Task Management** | Full CRUD -- create, read, update, delete tasks; mark tasks as complete or incomplete; filter and list operations |
| **AI Chatbot** | Natural language task management powered by Cohere (free tier); intent classification and routing; confirmation workflows for destructive actions |
| **Demo Mode** | Fully functional fallback when no API key is configured -- ideal for evaluation and testing |
| **Chat History** | Persistent conversation storage with per-user isolation |
| **Theming** | Dark and light theme support with system preference detection |
| **Responsive UI** | Mobile-first design with smooth Framer Motion animations |
| **Security** | Rate limiting on auth and task endpoints; input sanitization against prompt injection; CORS enforcement; no secrets in code |
| **Cloud Native** | Docker images, Docker Compose orchestration, Kubernetes manifests, and Helm charts for one-command deployment |

---

## Architecture Overview

```
+------------------+         +------------------+         +------------------+
|                  |  HTTP   |                  |  async   |                  |
|   Next.js 14     +-------->+   FastAPI 2.0    +--------->+  PostgreSQL 16   |
|   (Frontend)     |  :3000  |   (Backend)      |  :5432   |  (Database)      |
|                  |<--------+                  |<---------+                  |
+------------------+         +--------+---------+         +------------------+
                                      |
                                      | HTTPS
                                      v
                             +------------------+
                             |                  |
                             |   Cohere AI API  |
                             |   (Free Tier)    |
                             |                  |
                             +------------------+
```

**Request Flow:**

1. The browser sends requests to the Next.js frontend (port 3000).
2. The frontend proxies API calls to the FastAPI backend (port 8000).
3. The backend authenticates requests via JWT cookies, then queries PostgreSQL using async SQLAlchemy.
4. For AI chat requests, the backend sends the user message plus task context to Cohere, classifies the intent, and executes the corresponding task operation.
5. Responses flow back through the same path with structured JSON payloads.

**AI Pipeline:**

```
User Message --> Input Sanitizer --> Cohere AI Model --> Intent Classifier
                                                              |
              +-----------------------------------------------+
              |
              v
      +-------+--------+--------+---------+---------+
      |       |        |        |         |         |
    CREATE   LIST   COMPLETE  DELETE  UNCOMPLETE   INFO
      |       |        |        |         |         |
      v       v        v        v         v         v
   Task Executor (DB Operations)        Direct Response
      |
      v
   Formatted AI Response --> Frontend
```

---

## Tech Stack

### Backend

| Component | Technology | Version |
|---|---|---|
| Framework | FastAPI | >= 0.109.0 |
| Runtime | Python | 3.12 |
| ORM | SQLAlchemy (async) | >= 2.0.27 |
| DB Driver | asyncpg | >= 0.29.0 |
| Migrations | Alembic | >= 1.13.1 |
| Auth Tokens | python-jose (JWT/HS256) | >= 3.3.0 |
| Password Hashing | bcrypt | >= 4.1.2 |
| AI Provider | Cohere (free tier) | >= 5.0.0 |
| HTTP Client | httpx | >= 0.27.1 |
| Validation | Pydantic v2 | >= 2.12.3 |

### Frontend

| Component | Technology | Version |
|---|---|---|
| Framework | Next.js | 14.1.0 |
| UI Library | React | 18.2.0 |
| Language | TypeScript | 5.3+ |
| Styling | Tailwind CSS | 3.4+ |
| Animations | Framer Motion | 12.26+ |
| Icons | Lucide React | 0.562+ |
| Theming | next-themes | 0.4+ |

### Infrastructure

| Component | Technology | Purpose |
|---|---|---|
| Database | PostgreSQL 16 (Alpine) | Persistent data storage |
| Containerization | Docker | Application packaging |
| Orchestration | Docker Compose | Multi-service local deployment |
| Kubernetes | Minikube | Local cluster for K8s deployment |
| Package Manager | Helm 3 | Kubernetes application management |

---

## Project Structure

```
pakaura/
|
+-- api/                          # Backend service
|   +-- src/
|   |   +-- ai/                   # AI chatbot module
|   |   |   +-- agent.py          # AI agent orchestration
|   |   |   +-- client.py         # Cohere API client
|   |   |   +-- intent_router.py  # Intent classification and routing
|   |   |   +-- prompts.py        # System prompts for AI model
|   |   |   +-- sanitizer.py      # Input sanitization (anti-injection)
|   |   |   +-- schemas.py        # AI request/response models
|   |   |   +-- task_executor.py  # AI-to-database task bridge
|   |   |   +-- errors.py         # AI-specific error handling
|   |   +-- db/
|   |   |   +-- connection.py     # Async database session factory
|   |   |   +-- migrations/       # Alembic migration scripts
|   |   +-- middleware/
|   |   |   +-- auth.py           # JWT authentication middleware
|   |   |   +-- rate_limit.py     # Per-IP and per-user rate limiting
|   |   +-- models/
|   |   |   +-- user.py           # User SQLAlchemy model
|   |   |   +-- task.py           # Task SQLAlchemy model
|   |   |   +-- conversation.py   # Chat conversation model
|   |   |   +-- message.py        # Chat message model
|   |   +-- routes/
|   |   |   +-- auth.py           # Registration, login, logout
|   |   |   +-- tasks.py          # Task CRUD endpoints
|   |   |   +-- ai.py             # AI status and chat endpoints
|   |   |   +-- chat.py           # Chat history endpoints
|   |   +-- schemas/              # Pydantic request/response schemas
|   |   +-- services/             # Business logic services
|   |   +-- config.py             # Environment-based configuration
|   |   +-- main.py               # FastAPI application entry point
|   +-- tests/                    # Backend test suite
|   +-- requirements.txt          # Python dependencies
|
+-- frontend/                     # Frontend service
|   +-- src/
|   |   +-- app/
|   |   |   +-- (auth)/           # Auth pages (login, register)
|   |   |   +-- (protected)/      # Protected pages (dashboard, assistant)
|   |   |   +-- layout.tsx        # Root layout with theme provider
|   |   |   +-- page.tsx          # Landing page
|   |   +-- components/
|   |   |   +-- assistant/        # AI chatbot components
|   |   |   |   +-- ChatContainer.tsx
|   |   |   |   +-- ChatInput.tsx
|   |   |   |   +-- ChatMessage.tsx
|   |   |   |   +-- QuickActions.tsx
|   |   |   |   +-- ToolActions.tsx
|   |   |   +-- auth/             # Authentication forms
|   |   |   +-- tasks/            # Task list, task item, task form
|   |   |   +-- ui/               # Reusable UI primitives
|   |   +-- lib/                  # API client, auth helpers, chat utils
|   |   +-- types/                # TypeScript type definitions
|   |   +-- middleware.ts         # Next.js auth middleware
|   +-- tests/                    # Frontend test suite
|   +-- tailwind.config.ts        # Tailwind CSS configuration
|   +-- package.json
|
+-- infra/                        # Infrastructure
|   +-- docker/
|   |   +-- api.Dockerfile        # Backend container image
|   |   +-- frontend.Dockerfile   # Frontend container image
|   +-- docker-compose.yml        # Multi-service local orchestration
|   +-- helm/
|   |   +-- pakaura/
|   |       +-- Chart.yaml        # Helm chart metadata (v4.0.0)
|   |       +-- values.yaml       # Default Helm values
|   |       +-- values-local.yaml # Minikube-specific overrides
|   |       +-- templates/        # Kubernetes manifest templates
|   +-- kubernetes/               # Raw Kubernetes manifests
```

---

## Quick Start

### Prerequisites

| Tool | Minimum Version | Purpose |
|---|---|---|
| Python | 3.12 | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| PostgreSQL | 16 | Database |
| Docker | 24+ | Container builds |
| Docker Compose | 2.0+ | Multi-service orchestration |
| Minikube | 1.32+ | Local Kubernetes cluster (optional) |
| Helm | 3.14+ | Kubernetes package manager (optional) |

### Local Development

**1. Clone the repository**

```bash
git clone https://github.com/your-org/pakaura.git
cd pakaura
```

**2. Set up the backend**

```bash
cd api

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database URL and optional Cohere API key

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn src.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/api/docs` (development mode only).

**3. Set up the frontend**

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend is now available at `http://localhost:3000`.

**4. (Optional) Configure AI chatbot**

To enable the AI chatbot with live Cohere responses, obtain a free API key from [https://dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys) and set it in `api/.env`:

```env
COHERE_API_KEY=your-cohere-api-key-here
```

Without an API key, the chatbot runs in **demo mode** with intelligent keyword-based fallback responses.

---

### Docker Compose

Launch the entire stack (API, frontend, PostgreSQL) with a single command:

```bash
docker-compose -f infra/docker-compose.yml up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| PostgreSQL | localhost:5432 |

To stop all services:

```bash
docker-compose -f infra/docker-compose.yml down
```

To stop and remove all data volumes:

```bash
docker-compose -f infra/docker-compose.yml down -v
```

---

### Kubernetes (Minikube)

**1. Start Minikube and configure Docker**

```bash
minikube start --driver=docker
eval $(minikube docker-env)       # Linux/macOS
# minikube docker-env | Invoke-Expression   # Windows PowerShell
```

**2. Build images inside Minikube**

```bash
docker build -t pakaura-api:latest -f infra/docker/api.Dockerfile .
docker build -t pakaura-frontend:latest -f infra/docker/frontend.Dockerfile .
```

**3. Deploy with Helm**

```bash
helm install pakaura ./infra/helm/pakaura -f ./infra/helm/pakaura/values-local.yaml
```

**4. Access the application via port-forward**

```bash
# In separate terminals:
kubectl port-forward -n pakaura svc/frontend 3000:3000
kubectl port-forward -n pakaura svc/api 8000:8000
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |

**5. Uninstall**

```bash
helm uninstall pakaura
```

---

## Environment Variables

### Backend (`api/.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://localhost:5432/todo` | Yes | Async PostgreSQL connection string |
| `JWT_SECRET` | `change-this-secret-in-production` | Yes | Secret key for JWT token signing (min 32 chars in production) |
| `JWT_ALGORITHM` | `HS256` | No | JWT signing algorithm |
| `JWT_EXPIRATION_HOURS` | `24` | No | Token lifetime in hours |
| `FRONTEND_URL` | `http://localhost:3000` | Yes | Allowed CORS origin |
| `ENVIRONMENT` | `development` | No | Runtime environment (`development`, `production`) |
| `DEBUG` | `true` | No | Enable debug mode and API docs |
| `COHERE_API_KEY` | (empty) | No | Cohere API key; empty enables demo mode |
| `AI_MODEL` | `command-a-03-2025` | No | Cohere model identifier |
| `AI_TEMPERATURE` | `0.3` | No | Model temperature (0.0 - 1.0) |
| `AI_MAX_TOKENS` | `300` | No | Max tokens per AI response |
| `AI_TIMEOUT_SECONDS` | `30` | No | AI API request timeout |
| `AI_RATE_LIMIT_PER_MINUTE` | `30` | No | Per-user AI request rate limit |
| `RATE_LIMIT_AUTH_PER_MINUTE` | `10` | No | Per-IP auth endpoint rate limit |
| `RATE_LIMIT_TASKS_PER_MINUTE` | `100` | No | Per-user task endpoint rate limit |
| `COOKIE_SECURE` | `false` | No | Set `true` in production (requires HTTPS) |
| `COOKIE_SAMESITE` | `lax` | No | Cookie SameSite policy |

### Frontend

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## API Documentation

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user account | No |
| `POST` | `/api/v1/auth/login` | Authenticate and receive JWT cookie | No |
| `POST` | `/api/v1/auth/logout` | Clear authentication cookie | No |
| `GET` | `/api/v1/auth/me` | Get current authenticated user profile | Yes |

### Tasks

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/tasks` | List all tasks for the authenticated user | Yes |
| `POST` | `/api/v1/tasks` | Create a new task | Yes |
| `PATCH` | `/api/v1/tasks/{id}` | Update an existing task | Yes |
| `DELETE` | `/api/v1/tasks/{id}` | Delete a task | Yes |
| `POST` | `/api/v1/tasks/{id}/complete` | Mark a task as completed | Yes |
| `POST` | `/api/v1/tasks/{id}/uncomplete` | Mark a task as incomplete | Yes |

### AI Chatbot

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/ai/status` | Check AI service availability and mode | Yes |
| `POST` | `/api/v1/ai/chat` | Send a message to the AI assistant | Yes |
| `POST` | `/api/{user_id}/chat` | Send a chat message (legacy endpoint) | Yes |
| `GET` | `/api/{user_id}/chat/history` | Retrieve conversation history | Yes |

### System

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/health` | Health check (returns status, version, phase) | No |

### Error Response Format

All endpoints return errors in a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "details": []
  }
}
```

| HTTP Status | Error Code | Description |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid request data |
| 401 | `AUTHENTICATION_ERROR` | Missing or invalid JWT token |
| 404 | `NOT_FOUND` | Resource does not exist |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Database or external service down |

---

## AI Chatbot Guide

The AI assistant understands natural language commands for task management. It classifies user intent into one of nine categories and routes to the appropriate handler.

### Supported Commands

| Command | Example | What It Does |
|---|---|---|
| **List Tasks** | `"show all my tasks"` | Displays all current tasks with completion status |
| **Create Task** | `"add task buy groceries"` | Creates a new task with the specified title |
| **Complete Task** | `"complete task buy groceries"` | Marks the named task as done |
| **Uncomplete Task** | `"uncomplete task buy groceries"` | Reverts a completed task to active |
| **Delete Task** | `"delete task buy groceries"` | Removes the task (with confirmation prompt) |
| **Clear Completed** | `"clear completed tasks"` | Deletes all tasks marked as complete |
| **Get Help** | `"help"` | Shows available commands and usage tips |

### Intent Classification

The AI model classifies each message into one of these intents:

| Intent | Description |
|---|---|
| `CREATE` | User wants to add a new task |
| `LIST` | User wants to see their tasks |
| `COMPLETE` | User wants to mark a task as done |
| `UNCOMPLETE` | User wants to revert a completed task |
| `UPDATE` | User wants to modify a task |
| `DELETE` | User wants to remove a task |
| `CLARIFY` | The message is ambiguous; the AI asks a follow-up question |
| `ERROR` | An error occurred during processing |
| `INFO` | General informational response |

### Safety Features

- **Input Sanitization:** All user messages are sanitized to prevent prompt injection attacks before being sent to the AI model.
- **Delete Confirmation:** Destructive operations (delete) require explicit user confirmation before execution.
- **Rate Limiting:** AI endpoints are limited to 30 requests per user per minute.
- **Message Length Cap:** User messages are capped at 10,000 characters.
- **Demo Mode Fallback:** When the AI service is unavailable or unconfigured, the system falls back to keyword-based intent matching, ensuring uninterrupted functionality.

### Demo Mode

When no `COHERE_API_KEY` is configured, the chatbot operates in demo mode:

- Uses pattern matching to classify intents from keywords
- All task operations (create, list, complete, delete) remain fully functional
- No external API calls are made
- Ideal for testing, evaluation, and environments without internet access

---

## Screenshots

> Screenshots can be added to the `submission-final/screenshots/` directory.

| Screen | Description |
|---|---|
| `login.png` | Login page with dark/light theme toggle |
| `register.png` | User registration form |
| `dashboard.png` | Task dashboard with task list and completion controls |
| `assistant.png` | AI chatbot interface with quick action buttons |
| `chat-demo.png` | AI assistant conversation demonstrating task creation |
| `dark-theme.png` | Full application in dark mode |

---

## Testing

### Backend Tests

```bash
cd api
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Manual API Testing

With the backend running, visit `http://localhost:8000/api/docs` for Swagger UI (development mode only). You can test all endpoints interactively.

---

## Deployment Guide

### Production Checklist

Before deploying to production, ensure the following:

| Item | Action |
|---|---|
| JWT Secret | Set `JWT_SECRET` to a cryptographically random string (minimum 32 characters) |
| Cookie Security | Set `COOKIE_SECURE=true` (requires HTTPS) |
| CORS Origin | Set `FRONTEND_URL` to the production frontend domain |
| Debug Mode | Set `DEBUG=false` to disable Swagger docs exposure |
| Database | Use a managed PostgreSQL service with SSL connections |
| AI API Key | Set `COHERE_API_KEY` for live AI functionality |
| Rate Limits | Tune `RATE_LIMIT_*` variables for expected traffic |
| Environment | Set `ENVIRONMENT=production` |

### Kubernetes Production Deployment

1. Create a dedicated `values-production.yaml` with production-specific overrides.
2. Store secrets using Kubernetes Secrets or an external secrets manager.
3. Configure Ingress with TLS termination.
4. Set resource requests and limits in Helm values.
5. Enable horizontal pod autoscaling for the API service.

```bash
helm install pakaura ./infra/helm/pakaura \
  -f ./infra/helm/pakaura/values-production.yaml \
  --namespace pakaura \
  --create-namespace
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch from `main`.
3. Make changes following the existing code style and conventions.
4. Write tests for new functionality.
5. Ensure all existing tests pass.
6. Submit a pull request with a clear description of changes.

### Code Standards

- **Backend:** Follow PEP 8. Use type hints. All routes must have docstrings. Use async/await for database operations.
- **Frontend:** Follow TypeScript strict mode. Use functional components with hooks. Follow the existing component structure in `src/components/`.
- **Commits:** Use conventional commit messages (`feat:`, `fix:`, `docs:`, `refactor:`, etc.).

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Built with purpose for the hackathon by the PakAura Team.**
