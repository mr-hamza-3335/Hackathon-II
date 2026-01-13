/**
 * Premium Registration form with glassmorphism and animations.
 * PakAura Design System
 */
'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, AlertCircle, UserPlus, Check, X } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import { api, ApiError, validateRegistration } from '@/lib';
import { User } from '@/types';

export default function RegisterForm() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError('');

    const validation = validateRegistration(email, password);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }
    setErrors({});

    setLoading(true);
    try {
      await api.post<User>('/api/v1/auth/register', { email, password });
      router.push('/dashboard');
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.code === 'CONFLICT') {
          setErrors({ email: 'This email is already registered' });
        } else if (error.details.length > 0) {
          const fieldErrors: Record<string, string> = {};
          error.details.forEach((detail) => {
            fieldErrors[detail.field] = detail.message;
          });
          setErrors(fieldErrors);
        } else {
          setServerError(error.message);
        }
      } else {
        setServerError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Password strength calculation with requirements
  const passwordAnalysis = useMemo(() => {
    const requirements = [
      { label: 'At least 8 characters', met: password.length >= 8 },
      { label: 'Contains uppercase letter', met: /[A-Z]/.test(password) },
      { label: 'Contains lowercase letter', met: /[a-z]/.test(password) },
      { label: 'Contains number', met: /[0-9]/.test(password) },
      { label: 'Contains special character', met: /[^A-Za-z0-9]/.test(password) },
    ];

    const metCount = requirements.filter((r) => r.met).length;
    let strength = (metCount / requirements.length) * 100;
    let label = 'Weak';
    let color = 'bg-rose-500';

    if (strength >= 80) {
      label = 'Strong';
      color = 'bg-emerald-500';
    } else if (strength >= 60) {
      label = 'Good';
      color = 'bg-amber-500';
    } else if (strength >= 40) {
      label = 'Fair';
      color = 'bg-orange-500';
    }

    return { requirements, strength, label, color };
  }, [password]);

  return (
    <motion.div
      className="w-full"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Glass card */}
      <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-slate-200/50 dark:shadow-slate-900/50 border border-white/20 dark:border-slate-700/50 p-8 sm:p-10">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.h1
            className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-2"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            Create Account
          </motion.h1>
          <motion.p
            className="text-slate-500 dark:text-slate-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            Start organizing your tasks today
          </motion.p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Server error */}
          <AnimatePresence>
            {serverError && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                className="p-4 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/50 rounded-xl text-rose-700 dark:text-rose-300 text-sm flex items-center gap-3"
              >
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span>{serverError}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Input
              label="Email"
              type="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={errors.email}
              placeholder="you@example.com"
              autoComplete="email"
              required
              icon={<Mail className="w-5 h-5" />}
            />
          </motion.div>

          <motion.div
            className="space-y-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Input
              label="Password"
              type="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={errors.password}
              placeholder="Create a strong password"
              autoComplete="new-password"
              minLength={8}
              required
              icon={<Lock className="w-5 h-5" />}
            />

            {/* Password strength meter */}
            <AnimatePresence>
              {password.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-3 overflow-hidden"
                >
                  {/* Progress bar */}
                  <div className="space-y-1.5">
                    <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                      <motion.div
                        className={`h-full rounded-full ${passwordAnalysis.color}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${passwordAnalysis.strength}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-500 dark:text-slate-400">Password strength</span>
                      <span className={`font-semibold ${
                        passwordAnalysis.strength < 40 ? 'text-rose-500' :
                        passwordAnalysis.strength < 60 ? 'text-orange-500' :
                        passwordAnalysis.strength < 80 ? 'text-amber-500' : 'text-emerald-500'
                      }`}>
                        {passwordAnalysis.label}
                      </span>
                    </div>
                  </div>

                  {/* Requirements checklist */}
                  <div className="grid grid-cols-1 gap-1.5">
                    {passwordAnalysis.requirements.map((req, index) => (
                      <motion.div
                        key={req.label}
                        className="flex items-center gap-2 text-xs"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        {req.met ? (
                          <Check className="w-3.5 h-3.5 text-emerald-500" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-slate-300 dark:text-slate-600" />
                        )}
                        <span className={req.met ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'}>
                          {req.label}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Button
              type="submit"
              fullWidth
              size="lg"
              loading={loading}
              disabled={loading}
              icon={!loading ? <UserPlus className="w-5 h-5" /> : undefined}
              iconPosition="right"
            >
              Create Account
            </Button>
          </motion.div>
        </form>

        {/* Footer */}
        <motion.div
          className="mt-8 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Already have an account?{' '}
            <Link
              href="/login"
              className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold transition-colors"
            >
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
}
