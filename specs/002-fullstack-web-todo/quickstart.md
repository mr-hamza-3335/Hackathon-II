# Quickstart Guide: Phase II Full-Stack Web Todo Application

**Feature**: 002-fullstack-web-todo
**Date**: 2026-01-08

This guide provides setup instructions for developing and running the Phase II application.

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13+ | API backend |
| Node.js | 20+ LTS | Frontend build |
| npm | 10+ | Package management |
| Docker | Latest | Local development (optional) |
| Git | Latest | Version control |

### External Services

| Service | Purpose | Setup |
|---------|---------|-------|
| Neon PostgreSQL | Database | Create project at neon.tech |

---

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd hackathon-2
git checkout 002-fullstack-web-todo
```

### 2. Neon Database Setup

1. Go to [neon.tech](https://neon.tech) and create a project
2. Create a database named `todo`
3. Copy the connection string

### 3. Environment Variables

Create `.env` files in the project root (these are gitignored):

**api/.env**
```env
# Database
DATABASE_URL=postgresql://user:password@hostname/todo?sslmode=require

# Authentication
JWT_SECRET=your-secure-random-secret-at-least-32-chars
JWT_EXPIRY_HOURS=24

# CORS
FRONTEND_URL=http://localhost:3000

# Environment
ENV=development
```

**frontend/.env.local**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Backend Setup (FastAPI)

### Install Dependencies

```bash
cd api
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Required Python Packages

```txt
# api/requirements.txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy[asyncio]>=2.0.25
asyncpg>=0.29.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
alembic>=1.13.0
python-multipart>=0.0.6
httpx>=0.26.0  # For testing
pytest>=7.4.0
pytest-asyncio>=0.23.0
```

### Database Migrations

```bash
# Generate initial migration (first time only)
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Run Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: http://localhost:8000
Docs available at: http://localhost:8000/docs

---

## Frontend Setup (Next.js)

### Install Dependencies

```bash
cd frontend
npm install
```

### Required npm Packages

```json
{
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "react-dom": "18.x"
  },
  "devDependencies": {
    "typescript": "5.x",
    "@types/node": "20.x",
    "@types/react": "18.x",
    "@types/react-dom": "18.x",
    "tailwindcss": "3.x",
    "postcss": "8.x",
    "autoprefixer": "10.x",
    "jest": "29.x",
    "@testing-library/react": "14.x",
    "@testing-library/jest-dom": "6.x"
  }
}
```

### Run Development Server

```bash
npm run dev
```

Frontend available at: http://localhost:3000

---

## Docker Development (Alternative)

### Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### docker-compose.yml Structure

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET=${JWT_SECRET}
      - FRONTEND_URL=http://localhost:3000
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  db:
    image: postgres:16
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=todo
      - POSTGRES_USER=todo
      - POSTGRES_PASSWORD=todopassword
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Note**: Use local PostgreSQL for development. Production uses Neon Serverless.

---

## Running Tests

### Backend Tests

```bash
cd api

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_task_service.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

---

## Development Workflow

### 1. Start Services

```bash
# Terminal 1: Backend
cd api
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Verify Setup

1. Open http://localhost:3000 - should see landing page
2. Open http://localhost:8000/docs - should see API docs
3. Register a test user
4. Log in and verify dashboard loads

### 3. Database Management

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## API Endpoints Summary

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Log in user |
| POST | /api/auth/logout | Log out user |
| GET | /api/auth/me | Get current user |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | List user's tasks |
| POST | /api/tasks | Create task |
| GET | /api/tasks/{id} | Get task |
| PATCH | /api/tasks/{id} | Update task |
| DELETE | /api/tasks/{id} | Delete task |
| POST | /api/tasks/{id}/complete | Mark complete |
| POST | /api/tasks/{id}/uncomplete | Mark incomplete |

---

## Troubleshooting

### Common Issues

**Database connection failed**
- Verify DATABASE_URL is correct
- Check Neon project is active
- Ensure SSL mode is enabled for Neon

**CORS errors**
- Verify FRONTEND_URL in backend .env
- Ensure credentials: 'include' in frontend fetch calls
- Check browser console for specific errors

**JWT errors**
- Verify JWT_SECRET is set and consistent
- Check token expiration (24 hours default)
- Clear cookies and re-login

**Module not found (Python)**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Module not found (Node)**
- Run `npm install` in frontend directory
- Delete node_modules and reinstall if needed

---

## Project Structure Reference

```
hackathon-2/
├── backend/                 # [PROTECTED] Phase I console app
├── api/                     # Phase II FastAPI backend
│   ├── src/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── db/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Phase II Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   ├── tests/
│   ├── package.json
│   └── Dockerfile
├── infra/                   # Docker configuration
│   └── docker-compose.yml
├── specs/                   # Specifications
│   ├── 001-console-todo/
│   └── 002-fullstack-web-todo/
└── .specify/                # SDD templates
```

---

## Next Steps After Setup

1. Verify Phase I console app still works (`python backend/src/main.py`)
2. Run backend tests to ensure database connection
3. Run frontend tests to ensure components render
4. Test full registration → login → task CRUD flow
5. Review API documentation at /docs
