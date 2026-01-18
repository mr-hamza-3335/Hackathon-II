/**
 * Tool Actions display component.
 * Phase III: Shows tool calls made by the AI agent.
 */
'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronDown,
  ChevronUp,
  Wrench,
  Plus,
  List,
  CheckCircle,
  Trash2,
  Pencil,
} from 'lucide-react';
import { getToolDisplayName, getToolColorClass, type ActionTaken } from '@/lib/chat';

interface ToolActionsProps {
  actions: ActionTaken[];
}

// Map tool names to icons
const ToolIcons: Record<string, typeof Wrench> = {
  add_task: Plus,
  list_tasks: List,
  complete_task: CheckCircle,
  delete_task: Trash2,
  update_task: Pencil,
};

export function ToolActions({ actions }: ToolActionsProps) {
  const [expanded, setExpanded] = useState(false);

  if (!actions || actions.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-3"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
      >
        <Wrench className="w-4 h-4" />
        <span>
          {actions.length} action{actions.length > 1 ? 's' : ''} taken
        </span>
        {expanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 space-y-2 overflow-hidden"
          >
            {actions.map((action, idx) => {
              const IconComponent = ToolIcons[action.tool] || Wrench;
              const colorClass = getToolColorClass(action.tool);
              const displayName = getToolDisplayName(action.tool);
              const isSuccess = action.result?.success !== false;

              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 rounded-xl border ${
                    isSuccess
                      ? 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700'
                      : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <IconComponent className={`w-4 h-4 ${colorClass}`} />
                    <span className={`font-medium text-sm ${colorClass}`}>
                      {displayName}
                    </span>
                    <span
                      className={`ml-auto text-xs px-2 py-0.5 rounded-full ${
                        isSuccess
                          ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300'
                          : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                      }`}
                    >
                      {isSuccess ? 'Success' : 'Failed'}
                    </span>
                  </div>

                  {/* Result details */}
                  <div className="text-xs text-slate-600 dark:text-slate-400 font-mono overflow-x-auto">
                    <pre className="whitespace-pre-wrap break-all">
                      {JSON.stringify(action.result, null, 2)}
                    </pre>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default ToolActions;
