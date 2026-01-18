/**
 * ChatKit-style wrapper for Phase III chat interface.
 * Implements ChatKit patterns with OpenAI Agents SDK backend.
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
  Bot,
  User,
  Send,
  Loader2,
} from 'lucide-react';
import { ToolActions } from './ToolActions';
import { AssistantIcon } from './AssistantIcon';
import { QuickActions } from './QuickActions';
import { Button } from '@/components/ui';
import {
  sendChatMessage,
  getChatHistory,
  clearChatHistory,
  type ChatResponse,
  type ActionTaken,
} from '@/lib/chat';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: ActionTaken[];
  isLoading?: boolean;
  isError?: boolean;
}

interface ChatKitWrapperProps {
  userId: string;
  className?: string;
}

export function ChatKitWrapper({ userId, className = '' }: ChatKitWrapperProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Load chat history on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await getChatHistory(userId);
        if (history.messages.length > 0) {
          setConversationId(history.conversation_id);
          const loadedMessages: ChatMessage[] = history.messages.map((msg, idx) => ({
            id: `history-${idx}`,
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: new Date(),
          }));
          setMessages(loadedMessages);
        }
      } catch (err) {
        // Ignore history load errors - start fresh
        console.log('Starting fresh conversation');
      } finally {
        setIsInitialized(true);
      }
    };
    loadHistory();
  }, [userId]);

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
  const handleSend = async () => {
    const content = inputValue.trim();
    if (!content || isLoading) return;

    setError(null);
    setInputValue('');

    // Add user message
    const userMessage: ChatMessage = {
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
      const response: ChatResponse = await sendChatMessage(userId, content);

      // Update conversation ID
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Replace loading placeholder with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingId
            ? {
                id: loadingId,
                role: 'assistant',
                content: response.response,
                timestamp: new Date(),
                actions: response.actions_taken,
                isLoading: false,
              }
            : msg
        )
      );
    } catch (err: any) {
      // Handle 401 - redirect will happen automatically
      if (err.status === 401) {
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
                isError: true,
                isLoading: false,
              }
            : msg
        )
      );
      setError(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  // Handle quick action
  const handleQuickAction = (action: string) => {
    setInputValue(action);
    setTimeout(() => {
      handleSend();
    }, 100);
  };

  // Clear chat
  const handleClearChat = async () => {
    try {
      await clearChatHistory(userId);
      setMessages([]);
      setConversationId(null);
      setError(null);
    } catch (err) {
      // Just clear locally if API fails
      setMessages([]);
      setError(null);
    }
  };

  // Handle textarea auto-resize and keyboard
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
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
                  AI Task Assistant
                </h2>
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 text-xs font-medium"
                >
                  <Zap className="w-3 h-3" />
                  <span>OpenAI GPT-4o</span>
                </motion.div>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                Powered by OpenAI Agents SDK + MCP
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
      </motion.div>

      {/* Messages area */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-6 py-4 space-y-4 scroll-smooth bg-gradient-to-b from-slate-50/50 to-white dark:from-slate-900/50 dark:to-slate-950"
      >
        {!isInitialized ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
          </div>
        ) : messages.length === 0 ? (
          <EmptyState onQuickAction={handleQuickAction} />
        ) : (
          <>
            <AnimatePresence mode="popLayout">
              {messages.map((message) => (
                <ChatMessageBubble key={message.id} message={message} />
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
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message... (e.g., 'Add a task to buy groceries')"
              rows={1}
              disabled={isLoading}
              className="w-full px-4 py-3 pr-12 rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none transition-all disabled:opacity-50"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="p-3 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white shadow-lg shadow-emerald-500/25 hover:shadow-xl hover:shadow-emerald-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// Message bubble component
interface ChatMessageBubbleProps {
  message: ChatMessage;
}

function ChatMessageBubble({ message }: ChatMessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      layout
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`flex gap-3 max-w-[85%] ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}
      >
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser
              ? 'bg-slate-200 dark:bg-slate-700'
              : 'bg-gradient-to-br from-emerald-500 to-teal-500'
          }`}
        >
          {isUser ? (
            <User className="w-4 h-4 text-slate-600 dark:text-slate-300" />
          ) : (
            <Bot className="w-4 h-4 text-white" />
          )}
        </div>

        {/* Message content */}
        <div
          className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
        >
          <div
            className={`px-4 py-3 rounded-2xl ${
              isUser
                ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-br-md'
                : message.isError
                ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800 rounded-bl-md'
                : 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white border border-slate-200 dark:border-slate-700 shadow-sm rounded-bl-md'
            }`}
          >
            {message.isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-slate-500 dark:text-slate-400">
                  Thinking...
                </span>
              </div>
            ) : (
              <div className="whitespace-pre-wrap">{message.content}</div>
            )}
          </div>

          {/* Tool actions */}
          {!isUser && message.actions && message.actions.length > 0 && (
            <ToolActions actions={message.actions} />
          )}

          {/* Timestamp */}
          <span className="text-xs text-slate-400 mt-1">
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>
    </motion.div>
  );
}

// Empty state component
interface EmptyStateProps {
  onQuickAction: (action: string) => void;
}

function EmptyState({ onQuickAction }: EmptyStateProps) {
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
        Hi! I'm your AI Task Assistant
      </h3>
      <p className="text-slate-500 dark:text-slate-400 max-w-md mb-2">
        I can help you manage your tasks with natural language.
      </p>
      <p className="text-emerald-600 dark:text-emerald-400 text-sm mb-6">
        Powered by OpenAI GPT-4o + MCP Tools
      </p>

      {/* Quick actions */}
      <QuickActions onAction={onQuickAction} />
    </motion.div>
  );
}

export default ChatKitWrapper;
