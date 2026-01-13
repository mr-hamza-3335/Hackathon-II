/**
 * Premium EmptyState component with animations.
 * PakAura Design System
 */
'use client';

import { motion } from 'framer-motion';
import { ClipboardList, Sparkles, ArrowUp } from 'lucide-react';

export default function EmptyState() {
  return (
    <motion.div
      className="text-center py-16 px-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Animated illustration */}
      <motion.div
        className="relative mx-auto w-28 h-28 mb-8"
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        {/* Background glow */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-200/50 to-violet-200/50 dark:from-indigo-800/30 dark:to-violet-800/30 rounded-full blur-xl"></div>

        {/* Main circle */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-indigo-100 to-violet-100 dark:from-indigo-900/50 dark:to-violet-900/50 rounded-full"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Icon */}
        <div className="relative w-full h-full flex items-center justify-center">
          <ClipboardList className="w-12 h-12 text-indigo-500 dark:text-indigo-400" strokeWidth={1.5} />
        </div>

        {/* Floating decorations */}
        <motion.div
          className="absolute -top-2 -right-2 w-5 h-5 bg-gradient-to-br from-indigo-400 to-violet-400 dark:from-indigo-500 dark:to-violet-500 rounded-full shadow-lg"
          animate={{ y: [-4, 4, -4], x: [-2, 2, -2] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute -bottom-1 -left-1 w-4 h-4 bg-gradient-to-br from-violet-400 to-purple-400 dark:from-violet-500 dark:to-purple-500 rounded-full shadow-lg"
          animate={{ y: [4, -4, 4], x: [2, -2, 2] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
        />
        <motion.div
          className="absolute top-1/2 -right-4 w-3 h-3 bg-gradient-to-br from-emerald-400 to-teal-400 dark:from-emerald-500 dark:to-teal-500 rounded-full shadow-lg"
          animate={{ y: [-3, 3, -3] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        />
      </motion.div>

      {/* Text content */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <h3 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white mb-3 flex items-center justify-center gap-2">
          <Sparkles className="w-5 h-5 text-amber-500" />
          Your task list is empty
        </h3>
        <p className="text-slate-500 dark:text-slate-400 max-w-sm mx-auto mb-8 leading-relaxed">
          Start organizing your day by creating your first task. What would you like to accomplish?
        </p>
      </motion.div>

      {/* Visual hint */}
      <motion.div
        className="inline-flex items-center gap-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 px-5 py-2.5 rounded-full border border-indigo-100 dark:border-indigo-800/50"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <motion.div
          animate={{ y: [-2, 2, -2] }}
          transition={{ duration: 1, repeat: Infinity, ease: 'easeInOut' }}
        >
          <ArrowUp className="w-4 h-4" />
        </motion.div>
        <span>Add a task above to get started</span>
      </motion.div>

      {/* Bottom decorative line */}
      <motion.div
        className="mt-12 flex justify-center"
        initial={{ opacity: 0, scaleX: 0 }}
        animate={{ opacity: 1, scaleX: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <div className="w-32 h-1 bg-gradient-to-r from-transparent via-indigo-200 dark:via-indigo-800 to-transparent rounded-full"></div>
      </motion.div>
    </motion.div>
  );
}
