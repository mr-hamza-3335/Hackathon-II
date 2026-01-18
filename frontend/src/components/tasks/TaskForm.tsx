/**
 * Premium Task creation form with animations.
 * PakAura Design System
 */
'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Check, ClipboardList } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import { api, ApiError, validateTask } from '@/lib';
import { Task } from '@/types';

interface TaskFormProps {
  onTaskCreated: (task: Task) => void;
}

export default function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    const validation = validateTask(title);
    if (!validation.isValid) {
      setError(validation.errors.title || 'Invalid task title');
      return;
    }

    setLoading(true);
    try {
      const task = await api.post<Task>('/api/v1/tasks', { title: title.trim() });
      onTaskCreated(task);
      setTitle('');
      setSuccess(true);
      inputRef.current?.focus();
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      if (err instanceof ApiError) {
        // Don't show error for 401 - global auth handler will redirect
        if (err.status !== 401) {
          setError(err.message);
        }
      } else {
        setError('Failed to create task. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <Input
            ref={inputRef}
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              if (error) setError('');
            }}
            placeholder="What needs to be done?"
            error={error}
            maxLength={500}
            disabled={loading}
            icon={<ClipboardList className="w-5 h-5" />}
          />
        </div>
        <Button
          type="submit"
          loading={loading}
          disabled={loading || !title.trim()}
          variant={success ? 'success' : 'primary'}
          icon={success ? <Check className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
          className="whitespace-nowrap sm:w-auto w-full"
        >
          {success ? 'Added!' : 'Add Task'}
        </Button>
      </div>

      {/* Character count */}
      <AnimatePresence>
        {title.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex justify-end"
          >
            <span className={`text-xs ${
              title.length >= 450
                ? 'text-amber-500 dark:text-amber-400'
                : 'text-slate-400 dark:text-slate-500'
            }`}>
              {title.length}/500 characters
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </form>
  );
}
