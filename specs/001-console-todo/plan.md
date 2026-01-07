# Implementation Plan: Phase I Console Todo Application

**Branch**: `001-console-todo` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-todo/spec.md`

## Summary

Build a command-line Todo application in Python 3.13+ with in-memory storage. The application supports CRUD operations for tasks (add, list, update, delete) and completion status management. No external dependencies, no persistence, single-user operation.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (Python standard library only)
**Storage**: In-memory (Python list/dict data structures)
**Testing**: pytest (standard Python testing)
**Target Platform**: Cross-platform CLI (Windows, macOS, Linux)
**Project Type**: Single project (console application)
**Performance Goals**: <100ms response time, support 1000+ tasks in memory
**Constraints**: No persistence, no external dependencies, no authentication
**Scale/Scope**: Single user, single session, in-memory only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development Only | PASS | Spec created before implementation plan |
| II. Single Repository Rule | PASS | All code in single repo under `/backend` |
| III. Evolution Over Rewrite | PASS | Phase I is foundation - no prior code to preserve |
| IV. Single Source of Truth | PASS | Requirements in `/specs/001-console-todo/spec.md` |
| V. Clean Architecture | PASS | Structure follows `/backend` for backend logic |
| VI. Professional Quality Bar | PASS | Clean structure, no over-engineering |

### Phase I Constitution Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Python 3.13+ | PASS | Target version specified |
| In-memory storage only | PASS | No database, no file persistence |
| No external databases | PASS | Python dict/list only |
| No web UI | PASS | CLI only |
| No authentication | PASS | Single user, no auth |
| Support: Add, Update, Delete, List, Complete/Incomplete | PASS | All in spec |

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contract)
│   └── cli-commands.md  # Command interface specification
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point, REPL loop
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task entity definition
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Task CRUD operations
│   └── cli/
│       ├── __init__.py
│       ├── commands.py      # Command parsing and routing
│       └── display.py       # Output formatting
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_task.py
    │   └── test_task_service.py
    └── integration/
        ├── __init__.py
        └── test_cli.py
```

**Structure Decision**: Single project structure under `/backend` following Constitution Clean Architecture principle. This prepares for Phase II where backend logic will be extracted into FastAPI endpoints.

## Component Design

### Layer 1: Models (`backend/src/models/`)

**Task Entity** - Core data structure representing a todo item.

Responsibilities:
- Define task attributes (id, title, completed, created_at)
- Validate title constraints (1-500 characters, non-empty)
- Provide serialization for display

### Layer 2: Services (`backend/src/services/`)

**TaskService** - Business logic for task management.

Responsibilities:
- Maintain in-memory task storage (dict keyed by id)
- Generate unique task IDs (sequential integers)
- Implement CRUD operations
- Handle task not found errors
- Validate inputs before operations

Operations:
- `add_task(title: str) -> Task` - Create and store new task
- `list_tasks() -> List[Task]` - Return all tasks
- `get_task(id: int) -> Task` - Get single task by ID
- `update_task(id: int, title: str) -> Task` - Update task title
- `delete_task(id: int) -> bool` - Remove task
- `complete_task(id: int) -> Task` - Mark task complete
- `uncomplete_task(id: int) -> Task` - Mark task incomplete

### Layer 3: CLI (`backend/src/cli/`)

**Commands** - Parse user input and route to services.

Responsibilities:
- Parse command strings into action + arguments
- Validate command syntax
- Route to appropriate service method
- Handle errors and format responses

**Display** - Format output for terminal.

Responsibilities:
- Format task lists (with visual status indicators)
- Format success/error messages
- Format help text

### Layer 4: Main (`backend/src/main.py`)

**Application Entry Point** - REPL loop.

Responsibilities:
- Initialize TaskService
- Run read-eval-print loop
- Handle exit command
- Handle keyboard interrupt (Ctrl+C)

## Command Interface

| Command | Syntax | Description |
|---------|--------|-------------|
| add | `add <title>` | Add new task with given title |
| list | `list` | Show all tasks |
| complete | `complete <id>` | Mark task as complete |
| uncomplete | `uncomplete <id>` | Mark task as incomplete |
| update | `update <id> <new_title>` | Update task title |
| delete | `delete <id>` | Delete task |
| help | `help` | Show available commands |
| exit | `exit` | Exit application |

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| Empty title | "Error: Task title cannot be empty" |
| Title too long (>500 chars) | "Error: Task title must be 500 characters or less" |
| Task not found | "Error: Task with ID {id} not found" |
| Invalid command | "Error: Unknown command '{cmd}'. Type 'help' for available commands" |
| Invalid ID format | "Error: Task ID must be a number" |
| Missing arguments | "Error: Missing required argument. Usage: {command syntax}" |

## Complexity Tracking

> No violations - design follows constitution principles with minimal complexity.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Storage | Python dict | Simplest in-memory storage, O(1) lookup by ID |
| ID Generation | Sequential int | Simple, readable, sufficient for single-session use |
| Architecture | 3-layer (model/service/cli) | Clean separation, prepares for Phase II API layer |
| Dependencies | None | Constitution requires no external dependencies |

## Implementation Order

1. **Models** - Task entity with validation
2. **Services** - TaskService with all CRUD operations
3. **CLI Commands** - Command parsing and routing
4. **CLI Display** - Output formatting
5. **Main** - REPL loop and entry point
6. **Tests** - Unit tests for models and services, integration tests for CLI

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ID reuse after delete | Tasks could have duplicate IDs | Never reuse IDs - use max(existing_ids)+1 or counter |
| Large task lists slow down | Performance degradation | Dict storage provides O(1) operations |
| Unicode in titles | Display issues | Python 3 handles Unicode natively |
| Edge case: very long titles | Truncation needed? | Validate at input (500 char limit per spec) |
