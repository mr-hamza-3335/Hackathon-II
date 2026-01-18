/**
 * TypeScript types for AI Assistant.
 * Phase 3: AI-powered task management types
 */

// Intent classification types
export type Intent =
  | 'CREATE'
  | 'LIST'
  | 'COMPLETE'
  | 'UNCOMPLETE'
  | 'UPDATE'
  | 'DELETE'
  | 'CLARIFY'
  | 'ERROR'
  | 'INFO';

// Action types
export type ActionType = 'api_call' | 'none';

// AI action details
export interface AIAction {
  type: ActionType;
  endpoint?: string;
  method?: string;
  payload?: Record<string, unknown>;
}

// AI request payload
export interface AIRequest {
  message: string;
  conversation_id?: string;
}

// Task data in AI response
export interface AITaskData {
  id: string;
  title: string;
  completed: boolean;
  created_at?: string;
}

// AI response from backend
export interface AIResponse {
  intent: Intent;
  message: string;
  action: AIAction;
  data?: {
    task?: AITaskData;
    tasks?: AITaskData[];
    filter?: 'all' | 'completed' | 'incomplete';
    count?: number;
    task_id?: string;
    pending_action?: string;
    deleted_task_id?: string;
    deleted_task_title?: string;
    error_code?: string;
    recoverable?: boolean;
    suggestion?: string;
  } | null;
}

// AI status response
export interface AIStatusResponse {
  provider: 'cohere' | 'demo';
  demo_mode: boolean;
  configured: boolean;
  message: string;
}

// Chat message for UI
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  intent?: Intent;
  data?: AIResponse['data'];
  isLoading?: boolean;
  isError?: boolean;
}

// Chat state
export interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
  pendingConfirmation: {
    taskId: string;
    action: string;
  } | null;
}
