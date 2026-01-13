/**
 * Premium Button component with Framer Motion animations.
 * PakAura Design System
 */
'use client';

import { ButtonHTMLAttributes, forwardRef } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'ref'> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'success' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled,
      className = '',
      icon,
      iconPosition = 'left',
      fullWidth = false,
      ...props
    },
    ref
  ) => {
    const baseStyles = `
      relative inline-flex items-center justify-center font-semibold rounded-xl
      transition-colors duration-200
      focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
      overflow-hidden
    `;

    const variantStyles = {
      primary: `
        bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600
        dark:from-indigo-500 dark:via-violet-500 dark:to-purple-500
        text-white shadow-lg
        hover:shadow-xl
        focus-visible:ring-indigo-500
      `,
      secondary: `
        bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200
        border border-slate-200 dark:border-slate-700
        hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300 dark:hover:border-slate-600
        hover:shadow-md
        focus-visible:ring-slate-400
      `,
      danger: `
        bg-gradient-to-r from-rose-600 to-red-600
        dark:from-rose-500 dark:to-red-500
        text-white shadow-lg
        hover:shadow-xl
        focus-visible:ring-rose-500
      `,
      ghost: `
        bg-transparent text-slate-600 dark:text-slate-300
        hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100
        focus-visible:ring-slate-400
      `,
      success: `
        bg-gradient-to-r from-emerald-600 to-teal-600
        dark:from-emerald-500 dark:to-teal-500
        text-white shadow-lg
        hover:shadow-xl
        focus-visible:ring-emerald-500
      `,
      outline: `
        bg-transparent border-2 border-indigo-500 dark:border-indigo-400
        text-indigo-600 dark:text-indigo-400
        hover:bg-indigo-50 dark:hover:bg-indigo-950
        focus-visible:ring-indigo-500
      `,
    };

    const sizeStyles = {
      sm: 'px-3.5 py-2 text-sm gap-1.5',
      md: 'px-5 py-2.5 text-sm gap-2',
      lg: 'px-6 py-3.5 text-base gap-2.5',
    };

    return (
      <motion.button
        ref={ref}
        disabled={disabled || loading}
        className={`
          ${baseStyles}
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${fullWidth ? 'w-full' : ''}
          ${className}
        `}
        whileHover={disabled || loading ? {} : { scale: 1.02, y: -2 }}
        whileTap={disabled || loading ? {} : { scale: 0.98 }}
        transition={{ type: 'spring', stiffness: 400, damping: 17 }}
        {...props}
      >
        {/* Shine effect overlay */}
        <motion.span
          className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none"
          initial={false}
        >
          <motion.span
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full"
            whileHover={{ translateX: '200%' }}
            transition={{ duration: 0.6, ease: 'easeInOut' }}
          />
        </motion.span>

        {/* Glow effect for primary buttons */}
        {variant === 'primary' && !disabled && (
          <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 opacity-0 group-hover:opacity-50 blur-xl transition-opacity duration-300" />
        )}

        {/* Content */}
        <span className="relative flex items-center gap-2">
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading...</span>
            </>
          ) : (
            <>
              {icon && iconPosition === 'left' && (
                <span className="flex-shrink-0">{icon}</span>
              )}
              {children}
              {icon && iconPosition === 'right' && (
                <span className="flex-shrink-0">{icon}</span>
              )}
            </>
          )}
        </span>
      </motion.button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
