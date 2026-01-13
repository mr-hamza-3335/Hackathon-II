# Data Model: Phase II Full-Stack Web Todo Application

**Feature**: 002-fullstack-web-todo
**Date**: 2026-01-08
**Status**: Complete

This document defines the database schema and entity relationships for Phase II.

---

## Entity Overview

```
┌─────────────────┐         ┌─────────────────┐
│      User       │         │      Task       │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │ 1     * │ id (PK)         │
│ email           │─────────│ user_id (FK)    │
│ password_hash   │         │ title           │
│ created_at      │         │ completed       │
│ updated_at      │         │ created_at      │
└─────────────────┘         │ updated_at      │
                            └─────────────────┘
```

**Relationship**: One User has many Tasks. Each Task belongs to exactly one User.

---

## Entity: User

Represents a registered user who can authenticate and manage tasks.

**Requirement References**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-007

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PK, NOT NULL, DEFAULT gen_random_uuid() | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (case-insensitive comparison) |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt-hashed password |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update time |

### Validation Rules

| Rule | Constraint | Error Code |
|------|------------|------------|
| Email required | NOT NULL | VALIDATION_ERROR |
| Email format | Valid email pattern | VALIDATION_ERROR |
| Email unique | UNIQUE constraint | CONFLICT |
| Email case-insensitive | LOWER(email) comparison | N/A (internal) |
| Password required | NOT NULL | VALIDATION_ERROR |
| Password min length | >= 8 characters (before hashing) | VALIDATION_ERROR |

### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| users_pkey | id | PRIMARY KEY | Unique lookup |
| users_email_key | email | UNIQUE | Email uniqueness, login lookup |
| idx_users_email_lower | LOWER(email) | BTREE | Case-insensitive email lookup |

### SQL Definition

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Case-insensitive email lookup index
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
```

---

## Entity: Task

Represents a todo item owned by a user.

**Requirement References**: FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-018

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PK, NOT NULL, DEFAULT gen_random_uuid() | Unique identifier (FR-010) |
| user_id | UUID | FK → users.id, NOT NULL, ON DELETE CASCADE | Owner reference (FR-018) |
| title | VARCHAR(500) | NOT NULL | Task description (FR-016) |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Task creation time |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last modification time |

### Validation Rules

| Rule | Constraint | Error Code |
|------|------------|------------|
| Title required | NOT NULL, non-empty | VALIDATION_ERROR |
| Title max length | <= 500 characters | VALIDATION_ERROR |
| User required | FK NOT NULL | VALIDATION_ERROR |
| User exists | FK constraint | NOT_FOUND |

### Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| tasks_pkey | id | PRIMARY KEY | Unique lookup |
| idx_tasks_user_id | user_id | BTREE | User's task list queries |
| idx_tasks_user_completed | (user_id, completed) | BTREE | Filtered task list queries |

### Foreign Key Behavior

- **ON DELETE CASCADE**: When a user is deleted, all their tasks are automatically removed.
- **ON UPDATE NO ACTION**: User ID changes are not expected.

### SQL Definition

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Ensure title is not empty
    CONSTRAINT tasks_title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
);

-- Index for user's task list queries (FR-008, FR-011)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Composite index for filtered queries
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

---

## State Transitions

### User States

```
[Visitor] --register--> [Registered User] --login--> [Authenticated User]
                                              ^              |
                                              |--<-logout----|
```

### Task States

```
[New] --create--> [Incomplete] --complete--> [Complete]
                       ^                          |
                       |-------uncomplete---------|

Any State --delete--> [Deleted]
Any State --update--> Same State (title changed)
```

---

## Query Patterns

### User Queries

| Operation | Query Pattern | Index Used |
|-----------|---------------|------------|
| Register | INSERT INTO users | N/A |
| Login | SELECT WHERE LOWER(email) = LOWER(?) | idx_users_email_lower |
| Get by ID | SELECT WHERE id = ? | users_pkey |

### Task Queries

| Operation | Query Pattern | Index Used |
|-----------|---------------|------------|
| List user's tasks | SELECT WHERE user_id = ? | idx_tasks_user_id |
| List by status | SELECT WHERE user_id = ? AND completed = ? | idx_tasks_user_completed |
| Get single task | SELECT WHERE id = ? AND user_id = ? | tasks_pkey + filter |
| Create task | INSERT INTO tasks | N/A |
| Update task | UPDATE WHERE id = ? AND user_id = ? | tasks_pkey + filter |
| Delete task | DELETE WHERE id = ? AND user_id = ? | tasks_pkey + filter |
| Toggle complete | UPDATE SET completed = NOT completed WHERE id = ? AND user_id = ? | tasks_pkey + filter |

**Security Note**: ALL task queries MUST include `user_id = ?` filter to enforce user isolation (FR-008).

---

## SQLAlchemy ORM Models

### Base Model

```python
# api/src/models/base.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### User Model

```python
# api/src/models/user.py
from sqlalchemy import Column, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Relationship
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_users_email_lower', 'email'),
    )
```

### Task Model

```python
# api/src/models/task.py
from sqlalchemy import Column, String, Boolean, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from .base import Base, TimestampMixin

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)

    # Relationship
    user = relationship("User", back_populates="tasks")

    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(title)) > 0", name="tasks_title_not_empty"),
        Index('idx_tasks_user_id', 'user_id'),
        Index('idx_tasks_user_completed', 'user_id', 'completed'),
    )
```

---

## Migration Strategy

### Initial Migration (001_initial_schema)

1. Create `users` table with all columns and indexes
2. Create `tasks` table with all columns, constraints, and indexes
3. No data migration needed (new database)

### Rollback

1. Drop `tasks` table (removes FK dependency first)
2. Drop `users` table

### Alembic Migration File Structure

```
api/src/db/migrations/
├── env.py
├── script.py.mako
└── versions/
    └── 001_initial_schema.py
```

---

## Pydantic Schemas (DTOs)

### User Schemas

```python
# api/src/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### Task Schemas

```python
# api/src/schemas/task.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: UUID
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    count: int
```

---

## TypeScript Types (Frontend)

```typescript
// frontend/src/types/auth.ts
export interface User {
  id: string;
  email: string;
  createdAt: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

// frontend/src/types/task.ts
export interface Task {
  id: string;
  title: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateTaskRequest {
  title: string;
}

export interface UpdateTaskRequest {
  title?: string;
  completed?: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}
```

---

## Data Integrity Rules

### Referential Integrity

- Tasks cannot exist without a valid user_id
- User deletion cascades to all user's tasks
- No orphan tasks allowed

### Business Rules

1. **Email uniqueness**: Case-insensitive comparison prevents "User@email.com" and "user@email.com" as separate accounts
2. **Title validation**: Must be 1-500 characters, cannot be empty or whitespace-only
3. **User isolation**: Tasks are always filtered by authenticated user_id

### Concurrency Handling

- **Last write wins**: Per Edge Case specification
- **No optimistic locking**: Not required for Phase II scope
- **Database handles race conditions**: Atomic updates via SQL

---

## Summary

| Entity | Table | Key Constraints | Relationships |
|--------|-------|-----------------|---------------|
| User | users | email UNIQUE, password_hash NOT NULL | Has many Tasks |
| Task | tasks | title NOT NULL (1-500), user_id FK | Belongs to User |

The data model satisfies all 18 task-related functional requirements (FR-009 through FR-026) and supports the security requirements for user isolation.
