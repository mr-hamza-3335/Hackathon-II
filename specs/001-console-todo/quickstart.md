# Quickstart: Phase I Console Todo Application

**Branch**: `001-console-todo` | **Date**: 2025-01-07

## Prerequisites

- Python 3.13 or higher installed
- Terminal/command prompt access

## Installation

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd hackathon-2

# No additional dependencies required - uses Python standard library only
```

## Running the Application

```bash
# From repository root
python backend/src/main.py
```

**Expected output**:
```
Todo Application v1.0.0
Type 'help' for available commands.

>
```

## Quick Demo (5 minutes)

### 1. Add Tasks

```
> add Buy groceries
Task added: [1] Buy groceries

> add Send email to boss
Task added: [2] Send email to boss

> add Call mom
Task added: [3] Call mom
```

### 2. List Tasks

```
> list
Tasks:
[1] [ ] Buy groceries
[2] [ ] Send email to boss
[3] [ ] Call mom
```

### 3. Complete a Task

```
> complete 2
Task [2] marked as complete: Send email to boss

> list
Tasks:
[1] [ ] Buy groceries
[2] [x] Send email to boss
[3] [ ] Call mom
```

### 4. Update a Task

```
> update 1 Buy groceries from Costco
Task [1] updated: Buy groceries from Costco

> list
Tasks:
[1] [ ] Buy groceries from Costco
[2] [x] Send email to boss
[3] [ ] Call mom
```

### 5. Delete a Task

```
> delete 3
Task [3] deleted: Call mom

> list
Tasks:
[1] [ ] Buy groceries from Costco
[2] [x] Send email to boss
```

### 6. Undo Completion

```
> uncomplete 2
Task [2] marked as incomplete: Send email to boss
```

### 7. Exit

```
> exit
Goodbye!
```

## Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `add <title>` | Add a new task | `add Buy milk` |
| `list` | Show all tasks | `list` |
| `complete <id>` | Mark task complete | `complete 1` |
| `uncomplete <id>` | Mark task incomplete | `uncomplete 1` |
| `update <id> <title>` | Update task title | `update 1 New title` |
| `delete <id>` | Delete a task | `delete 1` |
| `help` | Show commands | `help` |
| `exit` | Exit application | `exit` |

## Running Tests

```bash
# From repository root
python -m pytest backend/tests/ -v
```

## Notes

- All tasks are stored in memory and will be lost when the application exits
- Task IDs are sequential and never reused (even after deletion)
- This is Phase I - no authentication, no persistence, single user only

## Troubleshooting

**Python version error**:
```bash
# Check Python version
python --version
# Should show Python 3.13.x or higher
```

**Module not found**:
```bash
# Make sure you're in the repository root
# Make sure backend/src/ directory exists
```

## Next Steps

After completing Phase I, proceed to Phase II to add:
- Web interface (Next.js)
- API backend (FastAPI)
- Database persistence (PostgreSQL/Neon)
- User authentication
