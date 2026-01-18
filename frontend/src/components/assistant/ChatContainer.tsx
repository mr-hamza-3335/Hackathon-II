/**
 * Main chat container component for the AI Assistant.
 * PakAura Design System - Phase 3 AI Assistant
 * Powered by Cohere (FREE AI)
 */
'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Trash2,
  ChevronDown,
  Sparkles,
  AlertCircle,
  Zap,
  Info,
} from 'lucide-react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { QuickActions } from './QuickActions';
import { AssistantIcon } from './AssistantIcon';
import { Button } from '@/components/ui';
import { sendMessage, generateConversationId, getAIStatus } from '@/lib';
import type { ChatMessage as ChatMessageType, AIResponse, AIStatusResponse } from '@/types';

interface ChatContainerProps {
  className?: string;
}

export function ChatContainer({ className = '' }: ChatContainerProps) {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId] = useState(() => generateConversationId());
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Check AI status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await getAIStatus();
        setAiStatus(status);
      } catch (err: any) {
        // Don't show error for 401 - global auth handler will redirect
        if (err.status === 401) {
          return;
        }
        // Default to demo mode if status check fails
        setAiStatus({
          provider: 'demo',
          demo_mode: true,
          configured: false,
          message: 'AI assistant is in demo mode.',
        });
      }
    };
    checkStatus();
  }, []);

  // Scroll to bottom
  const scrollToBottom = useCallback((smooth = true) => {
    messagesEndRef.current?.scrollIntoView({
      behavior: smooth ? 'smooth' : 'auto',
    });
  }, []);

  // Track scroll position
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Auto-scroll on new messages
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Handle sending a message
  const handleSend = async (content: string) => {
    setError(null);

    // Add user message
    const userMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Add loading placeholder
    const loadingId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      {
        id: loadingId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isLoading: true,
      },
    ]);
    setIsLoading(true);

    try {
      const response: AIResponse = await sendMessage(content, conversationId);

      // Replace loading placeholder with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingId
            ? {
                id: loadingId,
                role: 'assistant',
                content: response.message,
                timestamp: new Date(),
                intent: response.intent,
                data: response.data,
                isLoading: false,
              }
            : msg
        )
      );
    } catch (err: any) {
      // Don't show error for 401 - global auth handler will redirect
      if (err.status === 401) {
        // Remove loading placeholder since we're redirecting
        setMessages((prev) => prev.filter((msg) => msg.id !== loadingId));
        return;
      }

      // Replace loading placeholder with error
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingId
            ? {
                id: loadingId,
                role: 'assistant',
                content: err.message || 'Something went wrong. Please try again.',
                timestamp: new Date(),
                intent: 'ERROR',
                isError: true,
                isLoading: false,
              }
            : msg
        )
      );
      setError(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle quick action
  const handleQuickAction = (action: string) => {
    handleSend(action);
  };

  // Clear chat
  const handleClearChat = () => {
    setMessages([]);
    setError(null);
  };

  // Get AI provider display info
  const getProviderBadge = () => {
    if (!aiStatus) return null;

    if (!aiStatus.configured || aiStatus.demo_mode) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 text-xs font-medium"
        >
          <Info className="w-3 h-3" />
          <span>Demo Mode</span>
        </motion.div>
      );
    }

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-xs font-medium"
      >
        <Zap className="w-3 h-3" />
        <span>Powered by Cohere (Free)</span>
      </motion.div>
    );
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex-shrink-0 px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <AssistantIcon size="md" animated />
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 dark:from-emerald-400 dark:via-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
                  PakAura Assistant
                </h2>
                {getProviderBadge()}
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                Your AI-powered task manager
              </p>
            </div>
          </div>

          {messages.length > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearChat}
              icon={<Trash2 className="w-4 h-4" />}
              className="hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/30 dark:hover:text-red-400"
            >
              Clear
            </Button>
          )}
        </div>

        {/* Demo mode info banner */}
        {(aiStatus?.demo_mode || !aiStatus?.configured) && aiStatus && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-3 p-3 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border border-amber-200 dark:border-amber-800"
          >
            <div className="flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="text-amber-800 dark:text-amber-200 font-medium">
                  Demo Mode Active
                </p>
                <p className="text-amber-600 dark:text-amber-400 mt-0.5">
                  Basic task commands work! For full AI capabilities, add your free{' '}
                  <a
                    href="https://dashboard.cohere.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-amber-700 dark:hover:text-amber-300"
                  >
                    Cohere API key
                  </a>
                  .
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Messages area */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-6 py-4 space-y-4 scroll-smooth bg-gradient-to-b from-slate-50/50 to-white dark:from-slate-900/50 dark:to-slate-950"
      >
        {messages.length === 0 ? (
          <EmptyState onQuickAction={handleQuickAction} demoMode={aiStatus?.demo_mode || !aiStatus?.configured} />
        ) : (
          <>
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Scroll to bottom button */}
      <AnimatePresence>
        {showScrollButton && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            onClick={() => scrollToBottom()}
            className="absolute bottom-28 right-8 p-2.5 rounded-full bg-white dark:bg-slate-800 shadow-lg border border-slate-200 dark:border-slate-700 hover:shadow-xl hover:scale-105 transition-all"
          >
            <ChevronDown className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Error banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="px-6"
          >
            <div className="flex items-center gap-2 px-4 py-3 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input area */}
      <div className="flex-shrink-0 px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl">
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}

interface EmptyStateProps {
  onQuickAction: (action: string) => void;
  demoMode?: boolean;
}

function EmptyState({ onQuickAction, demoMode }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="flex flex-col items-center justify-center h-full text-center px-4"
    >
      {/* Large animated icon */}
      <motion.div
        animate={{
          y: [0, -10, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="mb-8"
      >
        <AssistantIcon size="xl" animated />
      </motion.div>

      <h3 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 dark:from-emerald-400 dark:via-teal-400 dark:to-cyan-400 bg-clip-text text-transparent mb-3">
        Hi! I'm your AI Assistant
      </h3>
      <p className="text-slate-500 dark:text-slate-400 max-w-md mb-2">
        I can help you manage your tasks with natural language.
      </p>
      {demoMode && (
        <p className="text-amber-600 dark:text-amber-400 text-sm mb-6">
          Running in demo mode - basic commands available
        </p>
      )}
      {!demoMode && (
        <p className="text-emerald-600 dark:text-emerald-400 text-sm mb-6">
          Powered by Cohere AI (Free tier)
        </p>
      )}

      {/* Quick actions */}
      <QuickActions onAction={onQuickAction} />
    </motion.div>
  );
}

export default ChatContainer;
