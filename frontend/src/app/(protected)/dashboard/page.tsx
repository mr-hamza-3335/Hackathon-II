/**
 * Premium Dashboard with full-screen responsive layout.
 * PakAura Design System
 */
'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, CheckCircle2, ListTodo, AlertCircle, Sparkles } from 'lucide-react';
import Card, { CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { TaskForm, TaskList, EmptyState } from '@/components/tasks';
import { api, ApiError } from '@/lib';
import { Task, TaskListResponse } from '@/types';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchTasks() {
      try {
        const response = await api.get<TaskListResponse>('/api/v1/tasks');
        setTasks(response.tasks);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Failed to load tasks. Please refresh the page.');
        }
      } finally {
        setLoading(false);
      }
    }
    fetchTasks();
  }, []);

  const handleTaskCreated = (task: Task) => {
    setTasks((prev) => [task, ...prev]);
  };

  const handleTaskUpdate = (updatedTask: Task) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
  };

  const handleTaskDelete = (taskId: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  if (loading) {
    return (
      <div className="w-full max-w-6xl mx-auto space-y-6">
        {/* Stats skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-24 rounded-2xl" />
          ))}
        </div>

        {/* Task form skeleton */}
        <div className="skeleton h-40 rounded-2xl" />

        {/* Task list skeleton */}
        <div className="skeleton h-64 rounded-2xl" />
      </div>
    );
  }

  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.filter((t) => !t.completed).length;
  const totalCount = tasks.length;
  const progressPercentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6 lg:space-y-8">
      {/* Page Header */}
      <motion.div
        className="space-y-1"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
          {completedCount === totalCount && totalCount > 0 ? (
            <span className="flex items-center gap-2">
              <Sparkles className="w-7 h-7 text-amber-500" />
              All tasks completed!
            </span>
          ) : (
            'Dashboard'
          )}
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Manage your tasks and stay organized
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        className="grid grid-cols-1 sm:grid-cols-3 gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {/* Total Tasks */}
        <div className="bg-gradient-to-br from-indigo-500 to-violet-600 rounded-2xl p-5 text-white shadow-lg shadow-indigo-500/20 dark:shadow-indigo-500/10">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-indigo-100 text-sm font-medium">Total Tasks</p>
              <p className="text-3xl font-bold mt-1">{totalCount}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <ListTodo className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Completed */}
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl p-5 text-white shadow-lg shadow-emerald-500/20 dark:shadow-emerald-500/10">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-emerald-100 text-sm font-medium">Completed</p>
              <p className="text-3xl font-bold mt-1">{completedCount}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Progress */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">Progress</p>
              <p className="text-3xl font-bold text-slate-900 dark:text-white mt-1">{progressPercentage}%</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
              <div className="w-6 h-6 relative">
                <svg className="w-6 h-6 transform -rotate-90" viewBox="0 0 24 24">
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    className="text-indigo-200 dark:text-indigo-800"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeDasharray={62.83}
                    strokeDashoffset={62.83 - (62.83 * progressPercentage) / 100}
                    className="text-indigo-600 dark:text-indigo-400 transition-all duration-500"
                  />
                </svg>
              </div>
            </div>
          </div>
          <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercentage}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </div>
      </motion.div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        {/* Task Form - Left column on large screens */}
        <motion.div
          className="lg:col-span-1"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card variant="elevated" className="sticky top-24">
            <CardHeader>
              <CardTitle subtitle="What would you like to accomplish?">
                <span className="flex items-center gap-2">
                  <Plus className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  Add New Task
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <TaskForm onTaskCreated={handleTaskCreated} />
            </CardContent>
          </Card>
        </motion.div>

        {/* Task List - Right column spanning 2 columns */}
        <motion.div
          className="lg:col-span-2"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card variant="glass">
            <CardHeader
              action={
                totalCount > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300">
                      {pendingCount} pending
                    </span>
                    <span className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300">
                      {completedCount} done
                    </span>
                  </div>
                )
              }
            >
              <CardTitle subtitle={totalCount === 0 ? 'No tasks yet - create one above!' : `${totalCount} total tasks`}>
                <span className="flex items-center gap-2">
                  <ListTodo className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  Your Tasks
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Error message */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="p-4 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/50 rounded-xl text-rose-700 dark:text-rose-300 text-sm mb-4 flex items-center gap-3"
                  >
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <span>{error}</span>
                  </motion.div>
                )}
              </AnimatePresence>

              {tasks.length === 0 ? (
                <EmptyState />
              ) : (
                <TaskList
                  tasks={tasks}
                  onUpdate={handleTaskUpdate}
                  onDelete={handleTaskDelete}
                />
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
