/**
 * Quick action buttons for common AI commands.
 * PakAura Design System - Phase 3 AI Assistant
 */
'use client';

import { motion } from 'framer-motion';
import { List, Plus, CheckCircle, HelpCircle } from 'lucide-react';

interface QuickActionsProps {
  onAction: (action: string) => void;
}

const quickActions = [
  {
    label: 'Show my tasks',
    command: 'Show all my tasks',
    icon: List,
    color: 'from-blue-500 to-indigo-500',
  },
  {
    label: 'Add a task',
    command: 'Add a new task to buy groceries',
    icon: Plus,
    color: 'from-emerald-500 to-teal-500',
  },
  {
    label: 'Complete a task',
    command: 'Show my incomplete tasks',
    icon: CheckCircle,
    color: 'from-violet-500 to-purple-500',
  },
  {
    label: 'Help',
    command: 'What can you do?',
    icon: HelpCircle,
    color: 'from-amber-500 to-orange-500',
  },
];

export function QuickActions({ onAction }: QuickActionsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="w-full max-w-lg"
    >
      <p className="text-sm text-slate-500 dark:text-slate-400 mb-3 text-center">
        Try these quick actions:
      </p>
      <div className="grid grid-cols-2 gap-3">
        {quickActions.map((action, index) => {
          const Icon = action.icon;
          return (
            <motion.button
              key={action.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onAction(action.command)}
              className={`
                group relative flex items-center gap-3 px-4 py-3.5 rounded-xl
                bg-white dark:bg-slate-800/80 backdrop-blur-sm
                border border-slate-200 dark:border-slate-700
                shadow-sm hover:shadow-md
                transition-all duration-200
                text-left
              `}
            >
              {/* Gradient background on hover */}
              <div
                className={`
                  absolute inset-0 rounded-xl bg-gradient-to-r ${action.color}
                  opacity-0 group-hover:opacity-5 dark:group-hover:opacity-10
                  transition-opacity duration-200
                `}
              />

              {/* Icon */}
              <div
                className={`
                  relative w-10 h-10 rounded-lg bg-gradient-to-br ${action.color}
                  flex items-center justify-center shadow-sm
                  group-hover:shadow-md transition-shadow duration-200
                `}
              >
                <Icon className="w-5 h-5 text-white" />
              </div>

              {/* Label */}
              <span className="relative text-sm font-medium text-slate-700 dark:text-slate-200">
                {action.label}
              </span>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
}

export default QuickActions;
