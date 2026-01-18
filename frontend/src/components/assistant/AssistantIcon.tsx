/**
 * Beautiful animated AI Assistant icon.
 * PakAura Design System - Phase 3 AI Assistant
 */
'use client';

import { motion } from 'framer-motion';

interface AssistantIconProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  animated?: boolean;
  className?: string;
}

const sizeMap = {
  sm: { container: 'w-8 h-8', icon: 'w-4 h-4', spark: 'w-3 h-3', sparkIcon: 'w-1.5 h-1.5' },
  md: { container: 'w-12 h-12', icon: 'w-6 h-6', spark: 'w-4 h-4', sparkIcon: 'w-2.5 h-2.5' },
  lg: { container: 'w-16 h-16', icon: 'w-8 h-8', spark: 'w-5 h-5', sparkIcon: 'w-3 h-3' },
  xl: { container: 'w-20 h-20', icon: 'w-10 h-10', spark: 'w-6 h-6', sparkIcon: 'w-3.5 h-3.5' },
};

export function AssistantIcon({
  size = 'md',
  animated = true,
  className = '',
}: AssistantIconProps) {
  const sizes = sizeMap[size];

  return (
    <div className={`relative ${className}`}>
      {/* Outer glow effect */}
      <motion.div
        animate={animated ? {
          scale: [1, 1.1, 1],
          opacity: [0.5, 0.8, 0.5],
        } : {}}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className={`absolute inset-0 ${sizes.container} rounded-2xl bg-gradient-to-br from-emerald-500/30 via-teal-500/30 to-cyan-500/30 blur-lg`}
      />

      {/* Main icon container */}
      <motion.div
        animate={animated ? {
          rotate: [0, 5, -5, 0],
        } : {}}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className={`relative ${sizes.container} rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/25`}
      >
        {/* AI Brain Icon SVG */}
        <svg
          className={`${sizes.icon} text-white`}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Brain outline */}
          <path
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="rgba(255,255,255,0.1)"
          />
          {/* Neural network nodes */}
          <motion.circle
            cx="8"
            cy="10"
            r="1.5"
            fill="currentColor"
            animate={animated ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 0 }}
          />
          <motion.circle
            cx="16"
            cy="10"
            r="1.5"
            fill="currentColor"
            animate={animated ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
          />
          <motion.circle
            cx="12"
            cy="8"
            r="1.5"
            fill="currentColor"
            animate={animated ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
          />
          <motion.circle
            cx="12"
            cy="14"
            r="1.5"
            fill="currentColor"
            animate={animated ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 0.9 }}
          />
          <motion.circle
            cx="10"
            cy="16"
            r="1"
            fill="currentColor"
            animate={animated ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 1.2 }}
          />
          <motion.circle
            cx="14"
            cy="16"
            r="1"
            fill="currentColor"
            animate={animated ? { scale: [1, 1.3, 1] } : {}}
            transition={{ duration: 2, repeat: Infinity, delay: 1.5 }}
          />
          {/* Neural connections */}
          <path
            d="M8 10L12 8M12 8L16 10M8 10L12 14M16 10L12 14M12 14L10 16M12 14L14 16"
            stroke="currentColor"
            strokeWidth="1"
            strokeLinecap="round"
            opacity="0.7"
          />
        </svg>
      </motion.div>

      {/* Sparkle indicator */}
      <motion.div
        animate={animated ? {
          scale: [1, 1.3, 1],
          rotate: [0, 180, 360],
        } : {}}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className={`absolute -top-1 -right-1 ${sizes.spark} bg-gradient-to-br from-yellow-400 via-orange-400 to-pink-500 rounded-full flex items-center justify-center shadow-lg shadow-orange-400/50`}
      >
        {/* Star sparkle */}
        <svg
          className={`${sizes.sparkIcon} text-white`}
          viewBox="0 0 24 24"
          fill="currentColor"
        >
          <path d="M12 2L14.09 8.26L20 9.27L15.55 13.14L16.91 19.02L12 16L7.09 19.02L8.45 13.14L4 9.27L9.91 8.26L12 2Z" />
        </svg>
      </motion.div>
    </div>
  );
}

/**
 * Simple bot icon for chat messages.
 */
export function BotAvatar({ className = '' }: { className?: string }) {
  return (
    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-sm ${className}`}>
      <svg
        className="w-4 h-4 text-white"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" fill="rgba(255,255,255,0.15)" />
        <circle cx="9" cy="11" r="1.5" fill="currentColor" />
        <circle cx="15" cy="11" r="1.5" fill="currentColor" />
        <path d="M9 15C9 15 10.5 17 12 17C13.5 17 15 15 15 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    </div>
  );
}

/**
 * User avatar for chat messages.
 */
export function UserAvatar({ className = '' }: { className?: string }) {
  return (
    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-sm ${className}`}>
      <svg
        className="w-4 h-4 text-white"
        viewBox="0 0 24 24"
        fill="currentColor"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle cx="12" cy="8" r="4" />
        <path d="M4 20C4 16.6863 7.58172 14 12 14C16.4183 14 20 16.6863 20 20" />
      </svg>
    </div>
  );
}

export default AssistantIcon;
