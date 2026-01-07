# Research: Phase I Console Todo Application

**Branch**: `001-console-todo` | **Date**: 2025-01-07

## Research Summary

This document captures research decisions for the Phase I Console Todo Application. Given the simplicity of the requirements and the constraint of using only Python standard library, most decisions are straightforward.

## Decision 1: In-Memory Storage Structure

**Decision**: Use Python `dict` with integer keys for task storage.

**Rationale**:
- O(1) lookup, insert, and delete operations by task ID
- Native Python data structure - no external dependencies
- Simple to implement and understand
- Sufficient for 1000+ tasks per spec requirement

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| List with linear search | Simple | O(n) lookup by ID | Performance degrades with many tasks |
| OrderedDict | Maintains insertion order | Unnecessary complexity | Standard dict maintains order in Python 3.7+ |
| dataclasses + list | Type-safe | O(n) lookup | Dict provides better performance |

## Decision 2: Task ID Generation

**Decision**: Use sequential integers starting from 1, tracked by a counter that never decreases.

**Rationale**:
- Simple and readable (Task 1, Task 2, etc.)
- Counter never resets even after deletes - prevents ID reuse
- No need for UUID complexity in single-session application

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| UUID | Globally unique | Harder to type/remember | Overkill for CLI single-session app |
| Timestamp-based | Unique | Hard to type | User experience suffers |
| Reusable IDs | Efficient | Confusing when task 3 becomes new task 3 | User confusion |

## Decision 3: Command Parsing Approach

**Decision**: Simple string split with first word as command, rest as arguments.

**Rationale**:
- Matches user mental model: `command arg1 arg2`
- Easy to implement without external libraries
- Sufficient for 8 simple commands

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| argparse | Full-featured, standard library | Complex for simple REPL | Over-engineering |
| shlex | Handles quotes properly | Adds complexity | Simple split is sufficient |
| Custom parser | Full control | More code | Simple approach works |

## Decision 4: Task Title with Spaces

**Decision**: Everything after the command and ID (if applicable) is the title.

**Rationale**:
- `add Buy groceries from the store` → title is "Buy groceries from the store"
- `update 1 New title with spaces` → title is "New title with spaces"
- No need for quotes - more natural CLI experience

**Implementation**:
```
add <title>        → split[0] = "add", split[1:] joined = title
update <id> <title> → split[0] = "update", split[1] = id, split[2:] joined = title
```

## Decision 5: Output Formatting

**Decision**: Use simple ASCII characters for task status display.

**Rationale**:
- `[ ]` for incomplete, `[x]` for complete
- Works on all terminals without Unicode issues
- Clear visual distinction

**Display Format**:
```
[1] [ ] Buy groceries
[2] [x] Send email
[3] [ ] Call mom
```

## Decision 6: Error Handling Strategy

**Decision**: Catch specific exceptions and return user-friendly messages.

**Rationale**:
- Custom exceptions for domain errors (TaskNotFound, InvalidTitle)
- All errors display helpful messages with usage hints
- No stack traces shown to users

**Exception Hierarchy**:
- `TodoError` (base)
  - `TaskNotFoundError`
  - `InvalidTitleError`
  - `InvalidCommandError`

## Decision 7: Project Structure

**Decision**: Place code under `/backend/src/` with models, services, and cli packages.

**Rationale**:
- Follows Constitution Clean Architecture (`/backend` for backend logic)
- Prepares for Phase II where same models/services will be used by FastAPI
- Clear separation of concerns

## Decision 8: Testing Framework

**Decision**: Use pytest for testing.

**Rationale**:
- De facto standard for Python testing
- Simple syntax, powerful features
- Available via pip (development dependency, not runtime)

**Test Structure**:
- `tests/unit/` - Test models and services in isolation
- `tests/integration/` - Test CLI command processing end-to-end

## No Clarifications Needed

All technical decisions could be made based on:
1. Constitution requirements (Python 3.13+, no external deps, in-memory only)
2. Spec requirements (CRUD operations, 500 char limit, unique IDs)
3. Best practices for simple CLI applications

No NEEDS CLARIFICATION items remain.
