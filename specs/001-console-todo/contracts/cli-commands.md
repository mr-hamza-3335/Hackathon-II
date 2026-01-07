# CLI Commands Contract: Phase I Console Todo Application

**Branch**: `001-console-todo` | **Date**: 2025-01-07

## Overview

This document defines the command-line interface contract for the Phase I Todo application. All user interactions follow this specification.

## Command Syntax

```
<command> [arguments...]
```

- Commands are case-insensitive
- Arguments are space-separated
- Titles with spaces do not require quotes

## Commands

### add

**Purpose**: Create a new task

**Syntax**:
```
add <title>
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| title | Yes | Task title (1-500 characters) |

**Success Response**:
```
Task added: [<id>] <title>
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| No title provided | `Error: Task title cannot be empty. Usage: add <title>` |
| Title > 500 chars | `Error: Task title must be 500 characters or less` |

**Examples**:
```
> add Buy groceries
Task added: [1] Buy groceries

> add Call mom about dinner plans
Task added: [2] Call mom about dinner plans

> add
Error: Task title cannot be empty. Usage: add <title>
```

---

### list

**Purpose**: Display all tasks

**Syntax**:
```
list
```

**Arguments**: None

**Success Response** (with tasks):
```
Tasks:
[<id>] [<status>] <title>
[<id>] [<status>] <title>
...
```

Where `<status>` is:
- `[ ]` for incomplete tasks
- `[x]` for completed tasks

**Success Response** (no tasks):
```
No tasks found. Use 'add <title>' to create one.
```

**Examples**:
```
> list
Tasks:
[1] [ ] Buy groceries
[2] [x] Send email
[3] [ ] Call mom

> list
No tasks found. Use 'add <title>' to create one.
```

---

### complete

**Purpose**: Mark a task as completed

**Syntax**:
```
complete <id>
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| id | Yes | Task ID (positive integer) |

**Success Response**:
```
Task [<id>] marked as complete: <title>
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| No ID provided | `Error: Missing task ID. Usage: complete <id>` |
| Invalid ID format | `Error: Task ID must be a number` |
| Task not found | `Error: Task with ID <id> not found` |

**Examples**:
```
> complete 1
Task [1] marked as complete: Buy groceries

> complete 999
Error: Task with ID 999 not found

> complete abc
Error: Task ID must be a number
```

---

### uncomplete

**Purpose**: Mark a task as incomplete

**Syntax**:
```
uncomplete <id>
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| id | Yes | Task ID (positive integer) |

**Success Response**:
```
Task [<id>] marked as incomplete: <title>
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| No ID provided | `Error: Missing task ID. Usage: uncomplete <id>` |
| Invalid ID format | `Error: Task ID must be a number` |
| Task not found | `Error: Task with ID <id> not found` |

**Examples**:
```
> uncomplete 1
Task [1] marked as incomplete: Buy groceries

> uncomplete 999
Error: Task with ID 999 not found
```

---

### update

**Purpose**: Change a task's title

**Syntax**:
```
update <id> <new_title>
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| id | Yes | Task ID (positive integer) |
| new_title | Yes | New title (1-500 characters) |

**Success Response**:
```
Task [<id>] updated: <new_title>
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| No ID provided | `Error: Missing arguments. Usage: update <id> <new_title>` |
| No title provided | `Error: New title cannot be empty. Usage: update <id> <new_title>` |
| Invalid ID format | `Error: Task ID must be a number` |
| Task not found | `Error: Task with ID <id> not found` |
| Title > 500 chars | `Error: Task title must be 500 characters or less` |

**Examples**:
```
> update 1 Buy groceries from Costco
Task [1] updated: Buy groceries from Costco

> update 1
Error: New title cannot be empty. Usage: update <id> <new_title>

> update 999 Something
Error: Task with ID 999 not found
```

---

### delete

**Purpose**: Remove a task

**Syntax**:
```
delete <id>
```

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|
| id | Yes | Task ID (positive integer) |

**Success Response**:
```
Task [<id>] deleted: <title>
```

**Error Responses**:
| Condition | Response |
|-----------|----------|
| No ID provided | `Error: Missing task ID. Usage: delete <id>` |
| Invalid ID format | `Error: Task ID must be a number` |
| Task not found | `Error: Task with ID <id> not found` |

**Examples**:
```
> delete 1
Task [1] deleted: Buy groceries

> delete 999
Error: Task with ID 999 not found
```

---

### help

**Purpose**: Display available commands

**Syntax**:
```
help
```

**Arguments**: None

**Response**:
```
Todo Application - Available Commands:

  add <title>           Add a new task
  list                  Show all tasks
  complete <id>         Mark task as complete
  uncomplete <id>       Mark task as incomplete
  update <id> <title>   Update task title
  delete <id>           Delete a task
  help                  Show this help message
  exit                  Exit the application

Examples:
  add Buy groceries
  complete 1
  update 1 Buy groceries from Costco
```

---

### exit

**Purpose**: Exit the application

**Syntax**:
```
exit
```

**Arguments**: None

**Response**:
```
Goodbye!
```

**Behavior**: Application terminates with exit code 0.

---

## Unknown Commands

**Response**:
```
Error: Unknown command '<command>'. Type 'help' for available commands.
```

**Example**:
```
> foo
Error: Unknown command 'foo'. Type 'help' for available commands.
```

## Application Startup

**Prompt**:
```
Todo Application v1.0.0
Type 'help' for available commands.

>
```

## Input Handling

- Empty input: Display prompt again (no error)
- Whitespace-only input: Display prompt again (no error)
- Ctrl+C: Display "Goodbye!" and exit gracefully
- Ctrl+D (EOF): Display "Goodbye!" and exit gracefully
