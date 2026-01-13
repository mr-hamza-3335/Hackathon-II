/**
 * TypeScript types for Task.
 * T023: Create TypeScript types for Task in frontend/src/types/task.ts per data-model.md
 */

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
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

export interface TaskError {
  error: {
    code: string;
    message: string;
    details: Array<{
      field: string;
      message: string;
    }>;
  };
}
