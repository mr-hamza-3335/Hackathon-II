/**
 * Premium protected layout with full-screen dashboard design.
 * PakAura Design System
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { LogOut, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui';
import { Logo } from '@/components/ui/Logo';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { getCurrentUser, logout } from '@/lib';
import { User } from '@/types';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    async function checkAuth() {
      try {
        const currentUser = await getCurrentUser();
        if (!currentUser) {
          router.push('/login');
          return;
        }
        setUser(currentUser);
      } catch (error) {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    }
    checkAuth();
  }, [router]);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logout();
      router.push('/login');
    } catch (error) {
      router.push('/login');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950/20">
        <motion.div
          className="flex flex-col items-center gap-4"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl border-4 border-indigo-100 dark:border-indigo-900"></div>
            <div className="absolute top-0 left-0 w-14 h-14 rounded-2xl border-4 border-indigo-500 border-t-transparent animate-spin"></div>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">Loading your workspace...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950/20">
      {/* Decorative background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-gradient-to-br from-indigo-400/20 to-violet-400/20 dark:from-indigo-600/10 dark:to-violet-600/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] bg-gradient-to-tr from-violet-400/20 to-purple-400/20 dark:from-violet-600/10 dark:to-purple-600/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 right-1/4 w-[300px] h-[300px] bg-gradient-to-br from-emerald-400/10 to-teal-400/10 dark:from-emerald-600/5 dark:to-teal-600/5 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <motion.header
        className="relative z-20 bg-white/70 dark:bg-slate-900/70 backdrop-blur-xl border-b border-slate-200/50 dark:border-slate-800/50 sticky top-0"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16 lg:h-18">
            {/* Logo */}
            <Logo size="md" />

            {/* User info & actions */}
            <div className="flex items-center gap-3 sm:gap-4">
              {/* Theme toggle */}
              <ThemeToggle />

              {/* User avatar & email */}
              {user && (
                <motion.div
                  className="hidden sm:flex items-center gap-3 px-4 py-2 rounded-xl bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200/50 dark:border-slate-700/50"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                    <span className="text-sm font-bold text-white">
                      {user.email.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-200 max-w-[150px] truncate">
                    {user.email}
                  </span>
                </motion.div>
              )}

              {/* Logout button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                disabled={loggingOut}
                icon={loggingOut ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogOut className="w-4 h-4" />}
              >
                <span className="hidden sm:inline">
                  {loggingOut ? 'Signing out...' : 'Sign Out'}
                </span>
              </Button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main content - Full screen */}
      <main className="relative z-10 w-full min-h-[calc(100vh-4rem)]">
        <AnimatePresence mode="wait">
          <motion.div
            className="w-full h-full px-4 sm:px-6 lg:px-8 py-6 lg:py-8"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer */}
      <motion.footer
        className="relative z-10 py-6 text-center border-t border-slate-200/30 dark:border-slate-800/30"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <p className="text-xs text-slate-400 dark:text-slate-500">
          PakAura &copy; {new Date().getFullYear()} &middot; Organize your day with clarity
        </p>
      </motion.footer>
    </div>
  );
}
