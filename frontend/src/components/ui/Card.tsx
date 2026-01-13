/**
 * Premium Card component with Framer Motion animations.
 * PakAura Design System
 */
'use client';

import { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'glass' | 'elevated' | 'gradient' | 'outline';
  hover?: boolean;
  animate?: boolean;
  delay?: number;
}

export default function Card({
  children,
  className = '',
  padding = 'md',
  variant = 'default',
  hover = false,
  animate = true,
  delay = 0,
}: CardProps) {
  const paddingStyles = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-10',
  };

  const variantStyles = {
    default: `
      bg-white dark:bg-slate-800/90
      border border-slate-200 dark:border-slate-700/50
      shadow-sm dark:shadow-slate-900/20
    `,
    glass: `
      bg-white/70 dark:bg-slate-800/50 backdrop-blur-xl
      border border-white/20 dark:border-slate-700/30
      shadow-xl shadow-slate-200/30 dark:shadow-slate-900/40
    `,
    elevated: `
      bg-white dark:bg-slate-800
      border border-slate-100 dark:border-slate-700/30
      shadow-xl shadow-slate-200/40 dark:shadow-slate-900/50
    `,
    gradient: `
      bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900
      border border-slate-200/60 dark:border-slate-700/50
      shadow-lg shadow-slate-200/30 dark:shadow-slate-900/30
    `,
    outline: `
      bg-transparent
      border-2 border-slate-200 dark:border-slate-700
    `,
  };

  const hoverStyles = hover
    ? 'cursor-pointer'
    : '';

  const MotionDiv = motion.div;

  return (
    <MotionDiv
      className={`
        rounded-2xl
        ${variantStyles[variant]}
        ${paddingStyles[padding]}
        ${hoverStyles}
        ${className}
      `}
      initial={animate ? { opacity: 0, y: 20 } : false}
      animate={animate ? { opacity: 1, y: 0 } : false}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
      whileHover={hover ? {
        y: -4,
        boxShadow: '0 20px 40px -10px rgb(99 102 241 / 0.15)',
        borderColor: 'rgb(165 180 252 / 0.5)',
      } : {}}
    >
      {children}
    </MotionDiv>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}

export function CardHeader({ children, className = '', action }: CardHeaderProps) {
  return (
    <div className={`mb-5 ${action ? 'flex items-center justify-between' : ''} ${className}`}>
      <div>{children}</div>
      {action && <div>{action}</div>}
    </div>
  );
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
  subtitle?: string;
  gradient?: boolean;
}

export function CardTitle({ children, className = '', subtitle, gradient = false }: CardTitleProps) {
  return (
    <div className={className}>
      <h2 className={`text-xl font-bold tracking-tight ${
        gradient
          ? 'bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 dark:from-indigo-400 dark:via-violet-400 dark:to-purple-400 bg-clip-text text-transparent'
          : 'text-slate-900 dark:text-slate-100'
      }`}>
        {children}
      </h2>
      {subtitle && (
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{subtitle}</p>
      )}
    </div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return <div className={`text-slate-700 dark:text-slate-300 ${className}`}>{children}</div>;
}

interface CardFooterProps {
  children: ReactNode;
  className?: string;
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
  return (
    <div className={`mt-6 pt-4 border-t border-slate-100 dark:border-slate-700/50 ${className}`}>
      {children}
    </div>
  );
}
