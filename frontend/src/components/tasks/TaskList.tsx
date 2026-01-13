/**
 * Premium Task list with Framer Motion animations.
 * PakAura Design System
 */
'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { CheckCircle2 } from 'lucide-react';
import TaskItem from './TaskItem';
import { Task } from '@/types';

interface TaskListProps {
  tasks: Task[];
  onUpdate: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

export default function TaskList({ tasks, onUpdate, onDelete }: TaskListProps) {
  // Separate completed and incomplete tasks
  const incompleteTasks = tasks.filter(t => !t.completed);
  const completedTasks = tasks.filter(t => t.completed);

  return (
    <div className="space-y-6">
      {/* Incomplete tasks */}
      {incompleteTasks.length > 0 && (
        <div className="space-y-3">
          <AnimatePresence mode="popLayout">
            {incompleteTasks.map((task, index) => (
              <TaskItem
                key={task.id}
                task={task}
                onUpdate={onUpdate}
                onDelete={onDelete}
                index={index}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Completed tasks section */}
      {completedTasks.length > 0 && (
        <div className="space-y-3">
          {incompleteTasks.length > 0 && (
            <motion.div
              className="flex items-center gap-3 py-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-slate-700 to-transparent"></div>
              <span className="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center gap-1.5 px-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                Completed ({completedTasks.length})
              </span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-slate-700 to-transparent"></div>
            </motion.div>
          )}
          <AnimatePresence mode="popLayout">
            {completedTasks.map((task, index) => (
              <TaskItem
                key={task.id}
                task={task}
                onUpdate={onUpdate}
                onDelete={onDelete}
                index={incompleteTasks.length + index}
              />
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
