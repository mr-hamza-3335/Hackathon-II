# PakAura - AI-Powered Task Management

> **Hackathon Submission: Phase III AI Task Assistant**

A full-stack task management application with an AI-powered conversational assistant built using Cohere's FREE API tier.

## Overview

PakAura is a modern, production-ready task management system that combines a beautiful Next.js frontend with a FastAPI backend and AI-powered natural language task management. Users can manage tasks through both traditional UI controls and conversational AI commands.

## Key Features

### AI Assistant (Powered by Cohere FREE Tier)
- **Natural Language Task Management**: Add, complete, update, and delete tasks using plain English
- **General Conversation**: Chat about any topic - education, geography, greetings, and more
- **Demo Mode**: Works without API key for basic task commands
- **Persistent Chat History**: Conversations saved in PostgreSQL

### Task Management
- **Full CRUD Operations**: Create, read, update, delete tasks
- **Completion Tracking**: Mark tasks as complete/incomplete
- **Filter Views**: View all, completed, or pending tasks
- **Real-time Updates**: Instant UI feedback on all actions

### Security & Authentication
- **JWT Authentication**: Secure token-based auth with HTTP-only cookies
- **24-hour Sessions**: Auto-expiring tokens with refresh handling
- **Protected Routes**: Automatic redirect on token expiry

### UI/UX
- **Dark/Light Mode**: Full theme support
- **Responsive Design**: Works on desktop and mobile
- **Smooth Animations**: Framer Motion powered transitions
- **Modern Design**: Glass morphism, gradients, and shadows

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy (async) |
| **Database** | PostgreSQL (Neon) |
| **AI** | Cohere API (FREE tier, command-a-03-2025 model) |
| **Auth** | JWT with HTTP-only cookies, bcrypt |
| **Tools** | MCP-style tools (add_task, list_tasks, complete_task, delete_task, update_task) |

## Project Structure

```
hackathon-2/
├── api/                    # FastAPI Backend
│   ├── src/
│   │   ├── ai/            # Cohere AI client, agent, conversation service
│   │   ├── db/            # Database connection & migrations
│   │   ├── middleware/    # Auth, rate limiting
│   │   ├── models/        # SQLAlchemy models (User, Task, Conversation, Message)
│   │   ├── mcp_server/    # MCP-style tool operations
│   │   ├── routes/        # API endpoints (auth, tasks, chat, ai)
│   │   └── main.py        # FastAPI application entry
│   └── requirements.txt
│
├── frontend/               # Next.js Frontend
│   ├── src/
│   │   ├── app/           # Next.js app router pages
│   │   ├── components/    # React components (assistant, tasks, ui)
│   │   ├── lib/           # API client, auth, utilities
│   │   └── types/         # TypeScript type definitions
│   └── package.json
│
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon account)
- Cohere API key (optional - demo mode works without it)

### 1. Clone & Navigate
```bash
git clone <repo-url>
cd hackathon-2
```

### 2. Backend Setup
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your database URL and (optional) Cohere API key
```

### 3. Database Setup
```bash
# Run migrations
alembic upgrade head
```

### 4. Frontend Setup
```bash
cd ../frontend
npm install

# Create .env.local if needed
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd api
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` to use the application.

## Demo Commands

Try these commands in the AI chat:

| Command | Description |
|---------|-------------|
| `hello` | Greeting - AI responds naturally |
| `how are you` | General conversation |
| `tell me about Karachi` | Information request |
| `add task buy groceries` | Creates a new task |
| `show my tasks` | Lists all tasks |
| `complete buy groceries` | Marks task as complete |
| `delete buy groceries` | Removes the task |
| `help` | Shows available commands |

## Environment Variables

### Backend (.env)
```env
# Database (Required)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname

# JWT (Required)
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000

# AI Configuration (Optional - demo mode if empty)
COHERE_API_KEY=your-cohere-api-key
AI_MODEL=command-a-03-2025
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=300
AI_TIMEOUT_SECONDS=30
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/auth/logout` | POST | User logout |
| `/api/v1/tasks` | GET/POST | List/Create tasks |
| `/api/v1/tasks/{id}` | PATCH/DELETE | Update/Delete task |
| `/api/v1/ai/chat` | POST | AI chat endpoint |
| `/api/v1/ai/status` | GET | AI service status |
| `/api/{user_id}/chat` | POST | Persistent chat endpoint |
| `/api/v1/health` | GET | Health check |

## Hackathon Notes

### Architecture Decisions
1. **Cohere FREE Tier**: No OpenAI dependency - uses completely free AI API
2. **Stateless Backend**: All state persisted in PostgreSQL (works with serverless)
3. **MCP-style Tools**: Modular tool architecture for task operations
4. **Demo Mode**: Full functionality without API key for evaluation

### Key Innovations
- Dual-mode AI (task commands + general conversation)
- Persistent conversation history across sessions
- Intelligent intent detection with keyword NLP + AI fallback
- Graceful degradation to demo mode without API key

### Testing Performed
- All task commands (add, list, complete, delete, update)
- General conversation responses
- Demo mode functionality
- Authentication flow (login, logout, token expiry)
- Error handling (network, API, validation)

## License

MIT License - Built for Hackathon 2025

---

**Built with Spec-Driven Development (SDD) methodology**
