/**
 * Premium TaskItem with animations and dark mode support.
 * PakAura Design System
 */
'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Pencil, Trash2, Check, AlertCircle } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import { api, ApiError, validateTask } from '@/lib';
import { Task } from '@/types';

interface TaskItemProps {
  task: Task;
  onUpdate: (task: Task) => void;
  onDelete: (taskId: string) => void;
  index?: number;
}

export default function TaskItem({ task, onUpdate, onDelete, index = 0 }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCompleting, setIsCompleting] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleToggleComplete = async () => {
    setIsCompleting(true);
    setLoading(true);
    try {
      const endpoint = task.completed
        ? `/api/v1/tasks/${task.id}/uncomplete`
        : `/api/v1/tasks/${task.id}/complete`;

      const updatedTask = await api.post<Task>(endpoint);
      onUpdate(updatedTask);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
      setTimeout(() => setIsCompleting(false), 300);
    }
  };

  const handleSaveEdit = async () => {
    setError('');

    const validation = validateTask(editTitle);
    if (!validation.isValid) {
      setError(validation.errors.title || 'Invalid task title');
      return;
    }

    if (editTitle.trim() === task.title) {
      setIsEditing(false);
      return;
    }

    setLoading(true);
    try {
      const updatedTask = await api.patch<Task>(`/api/v1/tasks/${task.id}`, {
        title: editTitle.trim(),
      });
      onUpdate(updatedTask);
      setIsEditing(false);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setIsEditing(false);
    setError('');
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setLoading(true);
    try {
      await api.delete(`/api/v1/tasks/${task.id}`);
      onDelete(task.id);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSaveEdit();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: 100 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      layout
      className={`
        group relative flex items-start gap-4 p-4 sm:p-5
        bg-white dark:bg-slate-800/80 rounded-2xl border-2
        transition-all duration-300 ease-out
        ${isCompleting && !task.completed ? 'scale-[1.02]' : ''}
        ${task.completed
          ? 'border-emerald-200 dark:border-emerald-800/50 bg-emerald-50/50 dark:bg-emerald-950/20'
          : 'border-slate-100 dark:border-slate-700/50 hover:border-indigo-200 dark:hover:border-indigo-700/50 hover:shadow-lg hover:shadow-indigo-500/5 dark:hover:shadow-indigo-500/10'
        }
        ${loading ? 'opacity-70' : ''}
      `}
    >
      {/* Checkbox */}
      <motion.button
        onClick={handleToggleComplete}
        disabled={loading}
        className={`
          relative flex-shrink-0 w-6 h-6 mt-0.5 rounded-full border-2
          flex items-center justify-center
          transition-all duration-300 ease-out
          focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-indigo-500 dark:focus-visible:ring-offset-slate-900
          ${task.completed
            ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 border-emerald-500 shadow-lg shadow-emerald-500/25'
            : 'border-slate-300 dark:border-slate-600 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/30'
          }
        `}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        aria-label={task.completed ? 'Mark incomplete' : 'Mark complete'}
      >
        <AnimatePresence>
          {task.completed && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0 }}
            >
              <Check className="w-3.5 h-3.5 text-white" strokeWidth={3} />
            </motion.div>
          )}
        </AnimatePresence>
        {!task.completed && (
          <div className="w-2 h-2 rounded-full bg-slate-200 dark:bg-slate-600 group-hover:bg-indigo-300 dark:group-hover:bg-indigo-500 transition-colors" />
        )}
      </motion.button>

      {/* Task content */}
      <div className="flex-1 min-w-0">
        <AnimatePresence mode="wait">
          {isEditing ? (
            <motion.div
              key="editing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-3"
            >
              <Input
                ref={inputRef}
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={handleKeyDown}
                error={error}
                maxLength={500}
                placeholder="Task title..."
              />
              <div className="flex items-center gap-2">
                <Button size="sm" onClick={handleSaveEdit} disabled={loading}>
                  {loading ? 'Saving...' : 'Save'}
                </Button>
                <Button size="sm" variant="ghost" onClick={handleCancelEdit} disabled={loading}>
                  Cancel
                </Button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="display"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-1"
            >
              <p
                className={`
                  text-sm sm:text-base leading-relaxed break-words
                  transition-all duration-300
                  ${task.completed
                    ? 'text-slate-400 dark:text-slate-500 line-through decoration-emerald-400 dark:decoration-emerald-600 decoration-2'
                    : 'text-slate-700 dark:text-slate-200'
                  }
                `}
              >
                {task.title}
              </p>

              {/* Error message */}
              <AnimatePresence>
                {error && (
                  <motion.p
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    className="text-xs text-rose-600 dark:text-rose-400 flex items-center gap-1"
                  >
                    <AlertCircle className="w-3 h-3" />
                    {error}
                  </motion.p>
                )}
              </AnimatePresence>

              {/* Timestamp */}
              <p className="text-xs text-slate-400 dark:text-slate-500">
                {new Date(task.created_at).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Action buttons */}
      {!isEditing && (
        <motion.div
          className={`
            flex items-center gap-1 flex-shrink-0
            transition-opacity duration-200
            ${loading ? 'opacity-50' : 'opacity-0 group-hover:opacity-100'}
          `}
          initial={false}
          animate={{ opacity: loading ? 0.5 : undefined }}
        >
          <motion.button
            onClick={() => setIsEditing(true)}
            disabled={loading}
            className="p-2 rounded-xl text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            aria-label="Edit task"
          >
            <Pencil className="w-4 h-4" />
          </motion.button>
          <motion.button
            onClick={handleDelete}
            disabled={loading}
            className="p-2 rounded-xl text-slate-400 dark:text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/30 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            aria-label="Delete task"
          >
            <Trash2 className="w-4 h-4" />
          </motion.button>
        </motion.div>
      )}

      {/* Completion celebration effect */}
      <AnimatePresence>
        {isCompleting && !task.completed && (
          <motion.div
            className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-transparent" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
