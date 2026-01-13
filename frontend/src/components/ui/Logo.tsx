/**
 * PakAura Logo Component
 * Modern abstract mark combining a checkmark with an aura/circle motif.
 */
'use client';

import { motion } from 'framer-motion';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
}

const sizes = {
  sm: { icon: 24, text: 'text-lg' },
  md: { icon: 32, text: 'text-xl' },
  lg: { icon: 40, text: 'text-2xl' },
  xl: { icon: 56, text: 'text-3xl' },
};

export function Logo({ size = 'md', showText = true, className = '' }: LogoProps) {
  const { icon, text } = sizes[size];

  return (
    <motion.div
      className={`flex items-center gap-3 ${className}`}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Logo Mark */}
      <div className="relative">
        {/* Outer glow */}
        <div
          className="absolute inset-0 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 blur-lg opacity-50 dark:opacity-70"
          style={{ width: icon, height: icon }}
        />

        {/* Main icon container */}
        <motion.div
          className="relative rounded-xl bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 p-0.5 shadow-lg"
          style={{ width: icon, height: icon }}
          whileHover={{ scale: 1.05, rotate: 5 }}
          transition={{ type: 'spring', stiffness: 400, damping: 10 }}
        >
          <div className="w-full h-full rounded-[10px] bg-white dark:bg-slate-900 flex items-center justify-center">
            {/* Abstract checkmark with aura */}
            <svg
              width={icon * 0.6}
              height={icon * 0.6}
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* Aura circles */}
              <circle
                cx="12"
                cy="12"
                r="10"
                className="stroke-indigo-200 dark:stroke-indigo-800"
                strokeWidth="1"
                strokeDasharray="4 2"
              />
              <circle
                cx="12"
                cy="12"
                r="7"
                className="stroke-violet-300 dark:stroke-violet-700"
                strokeWidth="1.5"
              />

              {/* Checkmark */}
              <motion.path
                d="M8 12.5L11 15.5L16 9"
                className="stroke-indigo-600 dark:stroke-indigo-400"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.8, delay: 0.3 }}
              />
            </svg>
          </div>
        </motion.div>
      </div>

      {/* Logo Text */}
      {showText && (
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h1 className={`font-bold ${text} bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 dark:from-indigo-400 dark:via-violet-400 dark:to-purple-400 bg-clip-text text-transparent`}>
            PakAura
          </h1>
          <p className="text-[10px] text-slate-500 dark:text-slate-400 -mt-1 tracking-wider uppercase">
            Organize with clarity
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}
