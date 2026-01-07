# Tasks: Phase I Console Todo Application

**Input**: Design documents from `/specs/001-console-todo/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/cli-commands.md

**Tests**: Tests are included as the feature requires verification of all acceptance scenarios.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `backend/src/`, `backend/tests/` at repository root
- Paths follow plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per implementation plan in `backend/src/`
- [x] T002 [P] Create `backend/src/__init__.py` package marker
- [x] T003 [P] Create `backend/src/models/__init__.py` package marker
- [x] T004 [P] Create `backend/src/services/__init__.py` package marker
- [x] T005 [P] Create `backend/src/cli/__init__.py` package marker
- [x] T006 [P] Create `backend/tests/__init__.py` package marker
- [x] T007 [P] Create `backend/tests/unit/__init__.py` package marker
- [x] T008 [P] Create `backend/tests/integration/__init__.py` package marker

**Checkpoint**: Project structure ready - all packages initialized

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create custom exceptions (TodoError, TaskNotFoundError, InvalidTitleError) in `backend/src/models/exceptions.py`
- [x] T010 Create Task model class with validation in `backend/src/models/task.py`
- [x] T011 Create TaskService class with storage initialization in `backend/src/services/task_service.py`
- [x] T012 [P] Create display helper module with formatting functions in `backend/src/cli/display.py`
- [x] T013 Unit tests for Task model validation in `backend/tests/unit/test_task.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1)

**Goal**: Users can add tasks with titles to the todo list

**Independent Test**: Run app, add "Buy groceries", verify confirmation message with ID shown

**FR Mapping**: FR-001, FR-002, FR-008

### Implementation for User Story 1

- [x] T014 [US1] Implement `add_task(title)` method in `backend/src/services/task_service.py`
- [x] T015 [US1] Implement `add` command parser in `backend/src/cli/commands.py`
- [x] T016 [US1] Implement success/error display for add command in `backend/src/cli/display.py`
- [x] T017 [US1] Unit test for add_task service method in `backend/tests/unit/test_task_service.py`
- [x] T018 [US1] Integration test for add command in `backend/tests/integration/test_cli.py`

**Checkpoint**: User Story 1 complete - can add tasks and see confirmation

---

## Phase 4: User Story 2 - List All Tasks (Priority: P1)

**Goal**: Users can view all tasks with their status

**Independent Test**: Add 2-3 tasks, run list, verify all tasks shown with IDs and status

**FR Mapping**: FR-003

### Implementation for User Story 2

- [x] T019 [US2] Implement `list_tasks()` method in `backend/src/services/task_service.py`
- [x] T020 [US2] Implement `list` command parser in `backend/src/cli/commands.py`
- [x] T021 [US2] Implement task list display formatting in `backend/src/cli/display.py`
- [x] T022 [US2] Unit test for list_tasks service method in `backend/tests/unit/test_task_service.py`
- [x] T023 [US2] Integration test for list command (with tasks and empty) in `backend/tests/integration/test_cli.py`

**Checkpoint**: User Stories 1 & 2 complete - MVP achieved (add + list)

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Users can toggle task completion status

**Independent Test**: Add task, mark complete, list to verify [x], mark uncomplete, list to verify [ ]

**FR Mapping**: FR-004, FR-005

### Implementation for User Story 3

- [x] T024 [US3] Implement `complete_task(id)` method in `backend/src/services/task_service.py`
- [x] T025 [US3] Implement `uncomplete_task(id)` method in `backend/src/services/task_service.py`
- [x] T026 [US3] Implement `complete` command parser in `backend/src/cli/commands.py`
- [x] T027 [US3] Implement `uncomplete` command parser in `backend/src/cli/commands.py`
- [x] T028 [US3] Implement success/error display for complete/uncomplete in `backend/src/cli/display.py`
- [x] T029 [US3] Unit tests for complete/uncomplete service methods in `backend/tests/unit/test_task_service.py`
- [x] T030 [US3] Integration tests for complete/uncomplete commands in `backend/tests/integration/test_cli.py`

**Checkpoint**: User Story 3 complete - can track task completion

---

## Phase 6: User Story 4 - Update Task Title (Priority: P3)

**Goal**: Users can edit task titles

**Independent Test**: Add task, update title, list to verify new title shown

**FR Mapping**: FR-006, FR-008

### Implementation for User Story 4

- [x] T031 [US4] Implement `update_task(id, title)` method in `backend/src/services/task_service.py`
- [x] T032 [US4] Implement `update` command parser in `backend/src/cli/commands.py`
- [x] T033 [US4] Implement success/error display for update in `backend/src/cli/display.py`
- [x] T034 [US4] Unit test for update_task service method in `backend/tests/unit/test_task_service.py`
- [x] T035 [US4] Integration test for update command in `backend/tests/integration/test_cli.py`

**Checkpoint**: User Story 4 complete - can edit task titles

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Users can remove tasks from the list

**Independent Test**: Add task, delete it, list to verify it's gone

**FR Mapping**: FR-007

### Implementation for User Story 5

- [x] T036 [US5] Implement `delete_task(id)` method in `backend/src/services/task_service.py`
- [x] T037 [US5] Implement `delete` command parser in `backend/src/cli/commands.py`
- [x] T038 [US5] Implement success/error display for delete in `backend/src/cli/display.py`
- [x] T039 [US5] Unit test for delete_task service method in `backend/tests/unit/test_task_service.py`
- [x] T040 [US5] Integration test for delete command in `backend/tests/integration/test_cli.py`

**Checkpoint**: User Story 5 complete - all CRUD operations available

---

## Phase 8: Application Shell & Help

**Purpose**: REPL loop, help command, and application entry point

**FR Mapping**: FR-009, FR-010, FR-011

- [x] T041 Implement command router/dispatcher in `backend/src/cli/commands.py`
- [x] T042 Implement `help` command with usage text in `backend/src/cli/commands.py`
- [x] T043 Implement unknown command error handling in `backend/src/cli/commands.py`
- [x] T044 Create REPL loop in `backend/src/main.py`
- [x] T045 Implement `exit` command and graceful shutdown in `backend/src/main.py`
- [x] T046 Handle Ctrl+C and EOF gracefully in `backend/src/main.py`
- [x] T047 Integration test for help command in `backend/tests/integration/test_cli.py`
- [x] T048 Integration test for unknown command handling in `backend/tests/integration/test_cli.py`
- [x] T049 Integration test for exit command in `backend/tests/integration/test_cli.py`

**Checkpoint**: Application fully functional with all commands

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T050 Verify all error messages match CLI contract in `backend/src/cli/display.py`
- [x] T051 Add application startup banner in `backend/src/main.py`
- [x] T052 Run full test suite and fix any failures
- [x] T053 Validate against quickstart.md demo flow
- [x] T054 Verify Python 3.13+ compatibility

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 and US2 can proceed in parallel (if staffed)
  - US3, US4, US5 can proceed in parallel (if staffed)
- **Application Shell (Phase 8)**: Depends on all user story implementations
- **Polish (Phase 9)**: Depends on Phase 8 completion

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Add) | Foundational | US2 |
| US2 (List) | Foundational | US1 |
| US3 (Complete) | US1, US2 | US4, US5 |
| US4 (Update) | US1, US2 | US3, US5 |
| US5 (Delete) | US1, US2 | US3, US4 |

### Within Each User Story

- Service method before CLI command
- CLI command before display formatting
- Implementation before tests (per task, not TDD)

### Parallel Opportunities

**Phase 1 (Setup)**: T002-T008 can all run in parallel
**Phase 2 (Foundational)**: T012 can run in parallel with T009-T011
**Phases 3-7**: Service methods can be parallelized across stories if team capacity allows

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all package marker creations together:
Task: "Create backend/src/__init__.py"
Task: "Create backend/src/models/__init__.py"
Task: "Create backend/src/services/__init__.py"
Task: "Create backend/src/cli/__init__.py"
Task: "Create backend/tests/__init__.py"
Task: "Create backend/tests/unit/__init__.py"
Task: "Create backend/tests/integration/__init__.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add)
4. Complete Phase 4: User Story 2 (List)
5. **STOP and VALIDATE**: Test add + list independently
6. Deploy/demo if ready - this is the MVP!

### Full Implementation

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently
3. Add User Story 2 → Test independently → MVP!
4. Add User Story 3 → Test independently
5. Add User Story 4 → Test independently
6. Add User Story 5 → Test independently → Full CRUD!
7. Add Application Shell → Test independently
8. Polish → Demo ready

### Demo Checkpoints

| Checkpoint | What Works | Demo Script |
|------------|------------|-------------|
| After Phase 4 | Add + List | Add 3 tasks, list them |
| After Phase 5 | + Complete | Mark 1 complete, list to verify |
| After Phase 7 | Full CRUD | Update 1, delete 1, list |
| After Phase 8 | Full App | Run quickstart.md demo |

---

## Task Summary

| Phase | Task Count | Purpose |
|-------|------------|---------|
| Phase 1: Setup | 8 | Project structure |
| Phase 2: Foundational | 5 | Core model, service, exceptions |
| Phase 3: US1 Add | 5 | Add task functionality |
| Phase 4: US2 List | 5 | List tasks functionality |
| Phase 5: US3 Complete | 7 | Complete/uncomplete functionality |
| Phase 6: US4 Update | 5 | Update task functionality |
| Phase 7: US5 Delete | 5 | Delete task functionality |
| Phase 8: App Shell | 9 | REPL, help, exit |
| Phase 9: Polish | 5 | Final validation |
| **Total** | **54** | |

### Tasks Per User Story

| User Story | Tasks | Files Touched |
|------------|-------|---------------|
| US1 (Add) | 5 | task_service.py, commands.py, display.py, tests |
| US2 (List) | 5 | task_service.py, commands.py, display.py, tests |
| US3 (Complete) | 7 | task_service.py, commands.py, display.py, tests |
| US4 (Update) | 5 | task_service.py, commands.py, display.py, tests |
| US5 (Delete) | 5 | task_service.py, commands.py, display.py, tests |

---

## Notes

- All tasks include exact file paths
- [P] tasks can run in parallel within their phase
- [US#] tags map tasks to user stories for traceability
- Each user story checkpoint is independently testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
