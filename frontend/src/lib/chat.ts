/**
 * Chat API client for Phase III.
 * Uses Cohere AI backend with MCP-style tools.
 */

import { api } from './api';

// Chat API types
export interface ChatRequest {
  message: string;
}

export interface ActionTaken {
  tool: string;
  result: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  actions_taken: ActionTaken[];
  conversation_id: string;
}

export interface ChatHistoryResponse {
  conversation_id: string;
  messages: ChatHistoryMessage[];
  count: number;
}

export interface ChatHistoryMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls?: Record<string, unknown>;
}

/**
 * Send a chat message to the AI assistant.
 *
 * @param userId - The user's UUID
 * @param message - The natural language message to send
 * @returns Chat response with AI reply and actions taken
 */
export async function sendChatMessage(
  userId: string,
  message: string
): Promise<ChatResponse> {
  const request: ChatRequest = { message };
  return api.post<ChatResponse>(`/api/${userId}/chat`, request);
}

/**
 * Get chat history for a user.
 *
 * @param userId - The user's UUID
 * @param limit - Maximum number of messages to retrieve
 * @returns Chat history with messages
 */
export async function getChatHistory(
  userId: string,
  limit: number = 50
): Promise<ChatHistoryResponse> {
  return api.get<ChatHistoryResponse>(`/api/${userId}/chat/history?limit=${limit}`);
}

/**
 * Clear chat history for a user.
 *
 * @param userId - The user's UUID
 * @returns Success status
 */
export async function clearChatHistory(
  userId: string
): Promise<{ message: string; cleared: boolean }> {
  return api.delete<{ message: string; cleared: boolean }>(`/api/${userId}/chat/history`);
}

/**
 * Get the tool display name for UI.
 *
 * @param tool - Tool name from API
 * @returns Human-readable tool name
 */
export function getToolDisplayName(tool: string): string {
  const toolNames: Record<string, string> = {
    add_task: 'Create Task',
    list_tasks: 'List Tasks',
    complete_task: 'Complete Task',
    uncomplete_task: 'Uncomplete Task',
    delete_task: 'Delete Task',
    update_task: 'Update Task',
    clear_completed: 'Clear Completed',
  };
  return toolNames[tool] || tool;
}

/**
 * Get the tool icon name for UI.
 *
 * @param tool - Tool name from API
 * @returns Lucide icon name
 */
export function getToolIconName(tool: string): string {
  const toolIcons: Record<string, string> = {
    add_task: 'Plus',
    list_tasks: 'List',
    complete_task: 'CheckCircle',
    uncomplete_task: 'Circle',
    delete_task: 'Trash2',
    update_task: 'Pencil',
    clear_completed: 'Trash2',
  };
  return toolIcons[tool] || 'Wrench';
}

/**
 * Get the tool color class for UI.
 *
 * @param tool - Tool name from API
 * @returns Tailwind color class
 */
export function getToolColorClass(tool: string): string {
  const toolColors: Record<string, string> = {
    add_task: 'text-emerald-600 dark:text-emerald-400',
    list_tasks: 'text-blue-600 dark:text-blue-400',
    complete_task: 'text-indigo-600 dark:text-indigo-400',
    uncomplete_task: 'text-orange-600 dark:text-orange-400',
    delete_task: 'text-red-600 dark:text-red-400',
    update_task: 'text-amber-600 dark:text-amber-400',
    clear_completed: 'text-red-600 dark:text-red-400',
  };
  return toolColors[tool] || 'text-slate-600 dark:text-slate-400';
}
