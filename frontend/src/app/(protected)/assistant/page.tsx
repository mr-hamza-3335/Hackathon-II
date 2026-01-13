/**
 * AI Assistant page - Full-screen chat interface.
 * PakAura Design System - Phase 3 AI Assistant
 */
'use client';

import { motion } from 'framer-motion';
import { ChatContainer } from '@/components/assistant';

export default function AssistantPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-[calc(100vh-8rem)] w-full max-w-4xl mx-auto"
    >
      {/* Main chat card */}
      <div className="h-full glass-card overflow-hidden flex flex-col">
        <ChatContainer className="h-full" />
      </div>
    </motion.div>
  );
}
