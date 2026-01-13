# Todo API - FastAPI Backend

Phase II Full-Stack Todo Application - Python FastAPI Backend

## Requirements

- Python 3.11 or 3.12
- PostgreSQL 14+ (local or Neon serverless)

## Quick Start (Windows)

### 1. Open PowerShell and navigate to the api folder

```powershell
cd "C:\Users\Mak Tech\Desktop\hackathon 2\api"
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Create the `.env` file

Create a file named `.env` in the `api` folder with:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/todo

# JWT Configuration
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Configuration
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Important**: Replace `yourpassword` with your actual PostgreSQL password.

### 6. Set up PostgreSQL database

#### Option A: Using local PostgreSQL

1. Open pgAdmin or psql
2. Create a new database:

```sql
CREATE DATABASE todo;
```

#### Option B: Using Docker

```powershell
docker run --name postgres-todo -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=todo -p 5432:5432 -d postgres:16-alpine
```

### 7. Run database migrations

```powershell
alembic upgrade head
```

### 8. Start the development server

```powershell
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### 9. Verify the server is running

Open your browser and go to:

- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/v1/health

You should see:
```json
{"status": "healthy", "version": "1.0.0"}
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/health` | Health check | No |
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login user | No |
| POST | `/api/v1/auth/logout` | Logout user | Yes |
| GET | `/api/v1/auth/me` | Get current user | Yes |
| GET | `/api/v1/tasks` | List user's tasks | Yes |
| POST | `/api/v1/tasks` | Create new task | Yes |
| GET | `/api/v1/tasks/{id}` | Get task by ID | Yes |
| PATCH | `/api/v1/tasks/{id}` | Update task | Yes |
| DELETE | `/api/v1/tasks/{id}` | Delete task | Yes |
| POST | `/api/v1/tasks/{id}/complete` | Mark complete | Yes |
| POST | `/api/v1/tasks/{id}/uncomplete` | Mark incomplete | Yes |

## Troubleshooting

### "bcrypt" import error

If you see `ModuleNotFoundError: No module named 'bcrypt'`:

```powershell
pip uninstall bcrypt
pip install bcrypt==4.1.2
```

### "email-validator" import error

If you see email validation errors:

```powershell
pip install email-validator==2.1.0.post1
```

### "asyncpg" connection error

Make sure:
1. PostgreSQL is running
2. DATABASE_URL uses `postgresql+asyncpg://` (NOT `postgresql://`)
3. Database `todo` exists

### "psycopg2" error

This project uses async PostgreSQL. Remove psycopg2:

```powershell
pip uninstall psycopg2 psycopg2-binary
```

### Alembic migration fails

Make sure DATABASE_URL is set correctly in `.env` and PostgreSQL is running.

### CORS errors in browser

Make sure `FRONTEND_URL` in `.env` matches your frontend URL exactly (e.g., `http://localhost:3000`).

## Project Structure

```
api/
├── src/
│   ├── main.py           # FastAPI application entry
│   ├── config.py         # Environment configuration
│   ├── db/
│   │   ├── connection.py # Async database connection
│   │   └── migrations/   # Alembic migrations
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response DTOs
│   ├── services/         # Business logic
│   ├── routes/           # API endpoints
│   └── middleware/       # Auth & rate limiting
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
├── alembic.ini          # Alembic configuration
└── .env                  # Environment variables (create this)
```

## Running Tests (Optional)

```powershell
pip install pytest pytest-asyncio httpx pytest-cov
pytest
```

## License

Hackathon II - Phase II Project
