/**
 * Premium Input component with modern styling and animations.
 * PakAura Design System
 */
'use client';

import { InputHTMLAttributes, forwardRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle } from 'lucide-react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, id, className = '', icon, iconPosition = 'left', onFocus, onBlur, ...props }, ref) => {
    const [isFocused, setIsFocused] = useState(false);
    const inputId = id || props.name;

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      onBlur?.(e);
    };

    return (
      <div className="w-full">
        {label && (
          <motion.label
            htmlFor={inputId}
            className={`
              block text-sm font-medium mb-2
              transition-colors duration-200
              ${isFocused ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-700 dark:text-slate-300'}
              ${error ? 'text-rose-600 dark:text-rose-400' : ''}
            `}
            animate={{ color: error ? '#e11d48' : isFocused ? '#4f46e5' : undefined }}
          >
            {label}
          </motion.label>
        )}
        <div className="relative group">
          {icon && iconPosition === 'left' && (
            <div className={`
              absolute left-3.5 top-1/2 -translate-y-1/2 z-10
              transition-colors duration-200
              ${isFocused ? 'text-indigo-500 dark:text-indigo-400' : 'text-slate-400 dark:text-slate-500'}
              ${error ? 'text-rose-400 dark:text-rose-400' : ''}
            `}>
              {icon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            onFocus={handleFocus}
            onBlur={handleBlur}
            className={`
              w-full px-4 py-3.5
              bg-white dark:bg-slate-800/80
              border-2 rounded-xl
              text-slate-900 dark:text-slate-100 text-sm
              placeholder-slate-400 dark:placeholder-slate-500
              transition-all duration-200 ease-out
              focus:outline-none focus:ring-0
              disabled:bg-slate-50 dark:disabled:bg-slate-800/50
              disabled:text-slate-400 dark:disabled:text-slate-500
              disabled:cursor-not-allowed
              ${error
                ? 'border-rose-300 dark:border-rose-500/50 focus:border-rose-500 dark:focus:border-rose-400 bg-rose-50/30 dark:bg-rose-950/20'
                : 'border-slate-200 dark:border-slate-700 focus:border-indigo-500 dark:focus:border-indigo-400 hover:border-slate-300 dark:hover:border-slate-600'
              }
              ${icon && iconPosition === 'left' ? 'pl-11' : ''}
              ${icon && iconPosition === 'right' ? 'pr-11' : ''}
              ${className}
            `}
            {...props}
          />
          {icon && iconPosition === 'right' && (
            <div className={`
              absolute right-3.5 top-1/2 -translate-y-1/2 z-10
              transition-colors duration-200
              ${isFocused ? 'text-indigo-500 dark:text-indigo-400' : 'text-slate-400 dark:text-slate-500'}
              ${error ? 'text-rose-400 dark:text-rose-400' : ''}
            `}>
              {icon}
            </div>
          )}

          {/* Animated focus ring */}
          <motion.div
            className="absolute inset-0 rounded-xl pointer-events-none"
            initial={false}
            animate={{
              boxShadow: isFocused && !error
                ? '0 0 0 4px rgba(99, 102, 241, 0.1)'
                : isFocused && error
                  ? '0 0 0 4px rgba(244, 63, 94, 0.1)'
                  : '0 0 0 0px rgba(99, 102, 241, 0)',
            }}
            transition={{ duration: 0.2 }}
          />
        </div>

        {/* Error or hint message with animation */}
        <AnimatePresence mode="wait">
          {(error || hint) && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className={`
                mt-2 text-sm flex items-center gap-1.5
                ${error ? 'text-rose-600 dark:text-rose-400' : 'text-slate-500 dark:text-slate-400'}
              `}
            >
              {error && (
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
              )}
              <span>{error || hint}</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
