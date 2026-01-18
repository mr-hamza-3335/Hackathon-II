/**
 * AI Assistant API client.
 * Phase 3: API functions for AI-powered task management
 */

import { api } from './api';
import type { AIRequest, AIResponse, AIStatusResponse } from '@/types';

const AI_ENDPOINTS = {
  CHAT: '/api/v1/ai/chat',
  STATUS: '/api/v1/ai/status',
} as const;

/**
 * Send a message to the AI assistant.
 *
 * @param message - The natural language message to send
 * @param conversationId - Optional conversation tracking ID
 * @returns AI response with intent, message, and optional data
 */
export async function sendMessage(
  message: string,
  conversationId?: string
): Promise<AIResponse> {
  const request: AIRequest = {
    message,
    conversation_id: conversationId,
  };

  return api.post<AIResponse>(AI_ENDPOINTS.CHAT, request);
}

/**
 * Check if the AI assistant is available and configured.
 *
 * @returns Status information about the AI service
 */
export async function getAIStatus(): Promise<AIStatusResponse> {
  return api.get<AIStatusResponse>(AI_ENDPOINTS.STATUS);
}

/**
 * Generate a unique conversation ID.
 *
 * @returns A new UUID for conversation tracking
 */
export function generateConversationId(): string {
  return crypto.randomUUID();
}

/**
 * Format a timestamp for display in chat.
 *
 * @param date - The date to format
 * @returns Formatted time string
 */
export function formatMessageTime(date: Date): string {
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  if (isToday) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  return date.toLocaleDateString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Get a color class based on intent type.
 *
 * @param intent - The AI intent
 * @returns Tailwind color class
 */
export function getIntentColor(intent?: string): string {
  switch (intent) {
    case 'CREATE':
      return 'text-emerald-600 dark:text-emerald-400';
    case 'COMPLETE':
    case 'UNCOMPLETE':
      return 'text-indigo-600 dark:text-indigo-400';
    case 'DELETE':
      return 'text-red-600 dark:text-red-400';
    case 'UPDATE':
      return 'text-amber-600 dark:text-amber-400';
    case 'LIST':
      return 'text-blue-600 dark:text-blue-400';
    case 'ERROR':
      return 'text-red-600 dark:text-red-400';
    case 'CLARIFY':
    case 'INFO':
    default:
      return 'text-slate-600 dark:text-slate-400';
  }
}

/**
 * Get an icon name based on intent type.
 *
 * @param intent - The AI intent
 * @returns Lucide icon name suggestion
 */
export function getIntentIconName(intent?: string): string {
  switch (intent) {
    case 'CREATE':
      return 'Plus';
    case 'COMPLETE':
      return 'CheckCircle';
    case 'UNCOMPLETE':
      return 'Circle';
    case 'DELETE':
      return 'Trash2';
    case 'UPDATE':
      return 'Pencil';
    case 'LIST':
      return 'List';
    case 'ERROR':
      return 'AlertCircle';
    case 'CLARIFY':
      return 'HelpCircle';
    case 'INFO':
      return 'Info';
    default:
      return 'MessageSquare';
  }
}
