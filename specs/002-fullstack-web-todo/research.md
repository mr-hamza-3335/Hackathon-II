# Research: Phase II Full-Stack Web Todo Application

**Feature**: 002-fullstack-web-todo
**Date**: 2026-01-08
**Status**: Complete

This document consolidates research findings for Phase II implementation decisions.

---

## 1. FastAPI Backend Architecture

### Decision: Layered Architecture Pattern

**Rationale**: The spec requires clean architecture (Core Principle V) with clear separation of concerns. A layered architecture provides maintainability, testability, and aligns with professional quality standards (Core Principle VI).

**Alternatives Considered**:
- **Flat structure**: All routes in single file. Rejected - doesn't scale, violates Clean Architecture.
- **Domain-driven design**: Overkill for a todo app with 2 entities.
- **Hexagonal architecture**: Too complex for current scope.

**Selected Pattern**:
```
api/src/
├── models/      # SQLAlchemy ORM entities
├── schemas/     # Pydantic DTOs (request/response)
├── services/    # Business logic (auth, tasks)
├── routes/      # HTTP endpoints
├── middleware/  # Cross-cutting (JWT validation)
└── db/          # Database connection, migrations
```

**Best Practices Applied**:
- Dependency injection via FastAPI's `Depends()`
- Async database operations with SQLAlchemy 2.0 async
- Pydantic v2 for validation and serialization
- Alembic for database migrations

---

## 2. Database Schema Design (Neon PostgreSQL)

### Decision: Two-Table Schema (Users + Tasks)

**Rationale**: Spec defines two key entities (User, Task) with a one-to-many relationship. Simple relational design satisfies all functional requirements without over-engineering.

**Alternatives Considered**:
- **Single table with JSON**: Rejected - violates normalization, poor query performance for user filtering.
- **Sessions table**: Not needed - JWT is stateless; logout invalidation handled client-side.
- **Soft deletes**: Not required by spec - hard deletes per FR-015.

**Schema Design**:
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for user-filtered queries (FR-008, FR-011)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
```

**Best Practices Applied**:
- UUIDs for IDs (prevents enumeration attacks)
- Timestamps with timezone for audit trail
- Foreign key with CASCADE delete (user deletion removes tasks)
- Index on user_id for query performance

---

## 3. Authentication Flow with JWT (Better Auth)

### Decision: Better Auth with HTTP-Only Cookie Storage

**Rationale**:
- Constitution mandates Better Auth with JWT.
- Spec clarifies tokens stored in HTTP-only cookies (Session 2026-01-08).
- HTTP-only cookies prevent XSS token theft (NFR-003).

**Alternatives Considered**:
- **localStorage**: Rejected - vulnerable to XSS.
- **Session-based auth**: Rejected - constitution requires JWT.
- **Custom JWT implementation**: Rejected - Better Auth is mandated.

**Authentication Flow**:

```
Registration Flow:
1. User submits email + password
2. Server validates (email format, password >= 8 chars)
3. Server checks email uniqueness (case-insensitive)
4. Server hashes password (bcrypt)
5. Server creates user record
6. Server issues JWT, sets HTTP-only cookie
7. Client redirects to dashboard

Login Flow:
1. User submits email + password
2. Server validates credentials
3. Server verifies password hash
4. Server issues JWT, sets HTTP-only cookie
5. Client redirects to dashboard

Logout Flow:
1. User clicks logout
2. Server clears HTTP-only cookie
3. Client redirects to login

Token Verification (every request):
1. Middleware extracts JWT from cookie
2. Middleware validates signature and expiry
3. Middleware extracts user_id, attaches to request
4. Route handler accesses user_id from request context
```

**JWT Configuration**:
- Algorithm: HS256 (symmetric, simple)
- Expiry: 24 hours (industry standard per Assumptions)
- Payload: `{ user_id, email, exp, iat }`
- Refresh: Not required for Phase II (out of scope)

**Best Practices Applied**:
- Secure password hashing with bcrypt (NFR-001)
- HTTP-only, Secure, SameSite cookies
- Generic error messages for auth failures (User Story 2, Scenario 2)
- Case-insensitive email comparison (Edge Case)

---

## 4. API Error Response Format

### Decision: Structured JSON Error Format

**Rationale**: Spec defines error format in FR-026 and clarifications.

**Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      { "field": "email", "message": "Email is required" },
      { "field": "password", "message": "Password must be at least 8 characters" }
    ]
  }
}
```

**Error Codes**:
| Code | HTTP Status | Usage |
|------|-------------|-------|
| VALIDATION_ERROR | 400 | Input validation failures |
| AUTHENTICATION_ERROR | 401 | Invalid/missing credentials |
| AUTHORIZATION_ERROR | 403 | Access to another user's resource |
| NOT_FOUND | 404 | Resource doesn't exist |
| CONFLICT | 409 | Email already registered |
| INTERNAL_ERROR | 500 | Unexpected server error |

**Best Practices Applied**:
- Field-level validation details for form UX
- Generic auth errors (don't reveal if email exists on login)
- Consistent format across all endpoints

---

## 5. Frontend Architecture (Next.js App Router)

### Decision: Next.js 14 App Router with Server Components

**Rationale**:
- Constitution mandates Next.js with App Router.
- Server Components reduce client bundle size.
- Route groups organize auth vs protected pages.

**Alternatives Considered**:
- **Pages Router**: Rejected - constitution specifies App Router.
- **Full client-side rendering**: Rejected - loses SSR benefits.
- **Separate SPA**: Rejected - Next.js provides better DX and SEO.

**Route Structure**:
```
src/app/
├── layout.tsx           # Root layout (providers)
├── page.tsx             # Landing → redirect based on auth
├── (auth)/              # Public auth routes
│   ├── login/page.tsx
│   └── register/page.tsx
└── (protected)/         # Requires authentication
    └── dashboard/page.tsx
```

**Data Fetching Strategy**:
- Auth pages: Client Components (form handling)
- Dashboard: Client Component with `useEffect` for API calls
- API calls via `fetch()` with credentials: 'include' (cookies)

**State Management**:
- Local component state for forms
- No global state library (not needed for scope)
- Auth state derived from API response

**Best Practices Applied**:
- Route groups for layout organization
- Middleware for auth redirects (server-side)
- TypeScript for type safety
- Tailwind CSS for responsive design (NFR-005)

---

## 6. Frontend-Backend Communication

### Decision: REST API with Fetch + HTTP-Only Cookies

**Rationale**:
- FR-025 requires RESTful API.
- Cookies automatically sent with `credentials: 'include'`.
- No token management code needed on client.

**API Client Pattern**:
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    credentials: 'include', // Send cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new ApiError(error);
  }

  return response.json();
}
```

**CORS Configuration (FastAPI)**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 7. Input Validation Strategy

### Decision: Dual Validation (Client + Server)

**Rationale**:
- Spec clarifies server is authoritative (Session 2026-01-08).
- Client validation for UX (immediate feedback, SC-006).
- Server revalidates everything (security).

**Validation Rules**:
| Field | Rule | Client | Server |
|-------|------|--------|--------|
| email | Valid email format | ✓ | ✓ |
| email | Unique (case-insensitive) | ✗ | ✓ |
| password | Min 8 characters | ✓ | ✓ |
| task.title | Non-empty | ✓ | ✓ |
| task.title | Max 500 characters | ✓ | ✓ |

**Implementation**:
- Client: HTML5 validation + custom validation functions
- Server: Pydantic models with validators

---

## 8. Security Considerations

### Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| SQL Injection | SQLAlchemy ORM (parameterized queries) |
| XSS | HTTP-only cookies, React auto-escaping |
| CSRF | SameSite cookie attribute |
| Password exposure | bcrypt hashing (NFR-001) |
| Enumeration | UUIDs, generic auth errors |
| Cross-user access | user_id filter on ALL task queries |

### Authentication Security Checklist

- [ ] Passwords hashed with bcrypt (cost factor 12)
- [ ] JWT signed with strong secret (environment variable)
- [ ] Cookies: HttpOnly, Secure, SameSite=Lax
- [ ] Generic error on login failure
- [ ] Rate limiting on auth endpoints (consider for production)

---

## 9. Testing Strategy

### Backend Tests (pytest)

**Unit Tests**:
- AuthService: password hashing, token generation
- TaskService: CRUD operations, user filtering

**Integration Tests**:
- Auth routes: registration, login, logout
- Task routes: full CRUD with auth
- Error handling: validation, authorization

**Fixtures**:
- Test database (separate from production)
- Authenticated user fixture
- Sample tasks fixture

### Frontend Tests (Jest + React Testing Library)

**Component Tests**:
- Form components: validation behavior
- Task components: render states

**E2E Tests** (optional, stretch):
- Registration → Login → Dashboard flow
- Task CRUD operations

---

## 10. Development Environment

### Docker Compose Stack

```yaml
services:
  api:
    build: ./api
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://...
      JWT_SECRET: ${JWT_SECRET}
    depends_on: [db]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: todo
      POSTGRES_USER: todo
      POSTGRES_PASSWORD: ${DB_PASSWORD}
```

**Note**: Production will use Neon Serverless PostgreSQL (external). Local Docker PostgreSQL for development/testing only.

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Backend structure | Layered (models/schemas/services/routes) | Clean Architecture |
| Database | Two tables (users, tasks) with UUID PKs | Simple, secure |
| Auth | Better Auth + JWT in HTTP-only cookies | Constitution + XSS protection |
| Error format | `{error: {code, message, details[]}}` | FR-026 specification |
| Frontend | Next.js 14 App Router + Tailwind | Constitution + responsive |
| API communication | REST + fetch + credentials cookies | Standard, simple |
| Validation | Dual (client UX, server authoritative) | Clarification from spec |
| Testing | pytest (API), Jest (Frontend) | Coverage for requirements |

All research complete. Ready for Phase 1: Design & Contracts.
