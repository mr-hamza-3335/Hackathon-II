/**
 * Chat message bubble component with premium animations.
 * PakAura Design System - Phase 3 AI Assistant
 */
'use client';

import { motion } from 'framer-motion';
import {
  User,
  Bot,
  Plus,
  CheckCircle,
  Circle,
  Trash2,
  Pencil,
  List,
  AlertCircle,
  HelpCircle,
  Info,
  Loader2,
  Check,
  X,
} from 'lucide-react';
import type { ChatMessage as ChatMessageType, Intent, AITaskData } from '@/types';
import { formatMessageTime, getIntentColor } from '@/lib';

interface ChatMessageProps {
  message: ChatMessageType;
  showTimestamp?: boolean;
}

const intentIcons: Record<Intent, typeof Plus> = {
  CREATE: Plus,
  COMPLETE: CheckCircle,
  UNCOMPLETE: Circle,
  DELETE: Trash2,
  UPDATE: Pencil,
  LIST: List,
  ERROR: AlertCircle,
  CLARIFY: HelpCircle,
  INFO: Info,
};

export function ChatMessage({ message, showTimestamp = true }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const Icon = message.intent ? intentIcons[message.intent] : undefined;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.1, type: 'spring', stiffness: 500 }}
        className={`
          flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center shadow-lg
          ${isUser
            ? 'bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-500'
            : 'bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500'
          }
        `}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </motion.div>

      {/* Message bubble */}
      <div className={`flex flex-col gap-1.5 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.05, type: 'spring', stiffness: 400 }}
          className={`
            relative px-4 py-3 rounded-2xl shadow-sm
            ${isUser
              ? 'bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-500 text-white rounded-tr-md'
              : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 rounded-tl-md'
            }
            ${message.isError ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-950/30' : ''}
          `}
        >
          {message.isLoading ? (
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
              <span className="text-slate-500 dark:text-slate-400 text-sm">Thinking...</span>
            </div>
          ) : (
            <>
              {/* Intent badge for assistant messages */}
              {!isUser && message.intent && Icon && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`flex items-center gap-1.5 text-xs font-medium mb-2 ${getIntentColor(message.intent)}`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span className="uppercase tracking-wide">{message.intent}</span>
                </motion.div>
              )}

              {/* Message content */}
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

              {/* Task data display */}
              {message.data?.tasks && message.data.tasks.length > 0 && (
                <TaskList tasks={message.data.tasks} />
              )}

              {message.data?.task && (
                <TaskCard task={message.data.task} intent={message.intent} />
              )}

              {/* Suggestion for errors */}
              {message.data?.suggestion && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="mt-2 text-xs text-slate-500 dark:text-slate-400 italic"
                >
                  {message.data.suggestion}
                </motion.p>
              )}
            </>
          )}
        </motion.div>

        {/* Timestamp */}
        {showTimestamp && !message.isLoading && (
          <span className="text-xs text-slate-400 dark:text-slate-500 px-1">
            {formatMessageTime(message.timestamp)}
          </span>
        )}
      </div>
    </motion.div>
  );
}

function TaskList({ tasks }: { tasks: AITaskData[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 }}
      className="mt-3 space-y-2"
    >
      {tasks.map((task, index) => (
        <motion.div
          key={task.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 + index * 0.05 }}
          className={`
            flex items-center gap-2 px-3 py-2 rounded-lg
            bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800
            ${task.completed ? 'opacity-60' : ''}
          `}
        >
          {task.completed ? (
            <Check className="w-4 h-4 text-emerald-500 flex-shrink-0" />
          ) : (
            <Circle className="w-4 h-4 text-slate-400 flex-shrink-0" />
          )}
          <span className={`text-sm ${task.completed ? 'line-through text-slate-500' : ''}`}>
            {task.title}
          </span>
        </motion.div>
      ))}
    </motion.div>
  );
}

function TaskCard({ task, intent }: { task: AITaskData; intent?: Intent }) {
  const isCreated = intent === 'CREATE';
  const isCompleted = intent === 'COMPLETE';
  const isDeleted = intent === 'DELETE';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.15 }}
      className={`
        mt-3 px-4 py-3 rounded-xl border
        ${isCreated
          ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800'
          : isCompleted
            ? 'bg-indigo-50 dark:bg-indigo-950/30 border-indigo-200 dark:border-indigo-800'
            : isDeleted
              ? 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800'
              : 'bg-slate-50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-700'
        }
      `}
    >
      <div className="flex items-center gap-2">
        {isCreated && <Plus className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />}
        {isCompleted && <CheckCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />}
        {isDeleted && <X className="w-4 h-4 text-red-600 dark:text-red-400" />}
        <span className={`text-sm font-medium ${isDeleted ? 'line-through' : ''}`}>
          {task.title}
        </span>
      </div>
    </motion.div>
  );
}

export default ChatMessage;
