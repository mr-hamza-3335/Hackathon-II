/**
 * AI Assistant page - Full-screen chat interface.
 * PakAura Design System - Phase 3 AI Assistant
 * Phase III Update: OpenAI Agents SDK + MCP integration
 */
'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { ChatKitWrapper } from '@/components/assistant';
import { getCurrentUser } from '@/lib';
import type { User } from '@/types';

export default function AssistantPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        // Auth error will be handled by global handler
        console.error('Failed to fetch user');
      } finally {
        setLoading(false);
      }
    }
    fetchUser();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-8rem)] w-full flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-[calc(100vh-8rem)] w-full flex items-center justify-center">
        <p className="text-slate-500 dark:text-slate-400">Please log in to use the AI assistant.</p>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-8rem)] w-full flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="w-full max-w-4xl h-[calc(100vh-10rem)] min-h-[500px]"
      >
        {/* Main chat card with premium glass effect */}
        <div className="h-full rounded-3xl bg-white/80 dark:bg-slate-900/80 backdrop-blur-2xl border border-slate-200/60 dark:border-slate-700/60 shadow-2xl shadow-emerald-500/5 dark:shadow-emerald-500/10 overflow-hidden flex flex-col relative">
          {/* Gradient glow effects */}
          <div className="absolute top-0 left-1/4 w-1/2 h-32 bg-gradient-to-b from-emerald-500/10 to-transparent blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 right-1/4 w-1/2 h-32 bg-gradient-to-t from-cyan-500/10 to-transparent blur-3xl pointer-events-none" />

          {/* Chat container with OpenAI Agents SDK */}
          <ChatKitWrapper userId={user.id} className="h-full relative z-10" />
        </div>
      </motion.div>
    </div>
  );
}
