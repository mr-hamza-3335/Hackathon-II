# Data Model: Phase I Console Todo Application

**Branch**: `001-console-todo` | **Date**: 2025-01-07

## Entity Overview

Phase I has a single entity: **Task**. All tasks are stored in memory and lost when the application exits.

## Task Entity

### Definition

```
Task
├── id: int (primary key, auto-generated)
├── title: str (required, 1-500 characters)
├── completed: bool (default: False)
└── created_at: datetime (auto-generated)
```

### Attributes

| Attribute | Type | Required | Default | Constraints |
|-----------|------|----------|---------|-------------|
| id | int | Yes (auto) | Auto-increment | Unique, positive integer, never reused |
| title | str | Yes | - | Non-empty, max 500 characters |
| completed | bool | No | False | True = complete, False = incomplete |
| created_at | datetime | Yes (auto) | Current time | Immutable after creation |

### Validation Rules

1. **Title Validation**:
   - MUST NOT be empty or whitespace-only
   - MUST NOT exceed 500 characters
   - Leading/trailing whitespace SHOULD be trimmed

2. **ID Validation**:
   - MUST be a positive integer
   - MUST be unique across all tasks in the session
   - MUST NOT be reused even after task deletion

### State Transitions

```
┌─────────────┐
│   Created   │ (completed = False)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│                                     │
▼                                     │
┌─────────────┐    complete()    ┌─────────────┐
│ Incomplete  │ ───────────────► │  Complete   │
│(completed=F)│                  │(completed=T)│
└─────────────┘ ◄─────────────── └─────────────┘
                  uncomplete()
```

## Storage Structure

### In-Memory Representation

```python
# TaskService internal storage
{
    tasks: Dict[int, Task],  # Key: task.id, Value: Task object
    next_id: int             # Counter for ID generation, starts at 1
}
```

### Example State

```python
{
    tasks: {
        1: Task(id=1, title="Buy groceries", completed=False, created_at=...),
        2: Task(id=2, title="Send email", completed=True, created_at=...),
        4: Task(id=4, title="Call mom", completed=False, created_at=...)
        # Note: id=3 was deleted, but 3 will never be reused
    },
    next_id: 5
}
```

## Operations

### Create (add_task)

```
Input: title (str)
Output: Task
Side Effects:
  - New Task added to storage
  - next_id incremented
Errors:
  - InvalidTitleError if title empty or >500 chars
```

### Read (list_tasks, get_task)

```
list_tasks:
  Input: None
  Output: List[Task] (all tasks, sorted by id)
  Side Effects: None

get_task:
  Input: id (int)
  Output: Task
  Errors: TaskNotFoundError if id not in storage
```

### Update (update_task)

```
Input: id (int), title (str)
Output: Task (updated)
Side Effects: Task title modified in storage
Errors:
  - TaskNotFoundError if id not found
  - InvalidTitleError if new title invalid
```

### Delete (delete_task)

```
Input: id (int)
Output: bool (True if deleted)
Side Effects: Task removed from storage
Errors: TaskNotFoundError if id not found
```

### Complete/Uncomplete

```
complete_task:
  Input: id (int)
  Output: Task (with completed=True)
  Side Effects: Task.completed set to True
  Errors: TaskNotFoundError if id not found

uncomplete_task:
  Input: id (int)
  Output: Task (with completed=False)
  Side Effects: Task.completed set to False
  Errors: TaskNotFoundError if id not found
```

## Phase II Evolution Note

In Phase II, this model will evolve to:
- Add `user_id` foreign key for multi-user support
- Persist to PostgreSQL database
- Add database migrations for schema changes

The current in-memory structure is designed to make this transition straightforward.
