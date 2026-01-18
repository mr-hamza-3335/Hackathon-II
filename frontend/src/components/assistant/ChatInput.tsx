/**
 * Chat input component with premium styling and animations.
 * PakAura Design System - Phase 3 AI Assistant
 */
'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, Mic, Sparkles } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  isLoading = false,
  placeholder = "Ask me anything about your tasks...",
}: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSubmit = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled && !isLoading) {
      onSend(trimmed);
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const canSend = message.trim().length > 0 && !disabled && !isLoading;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative"
    >
      {/* Glow effect on focus */}
      <AnimatePresence>
        {isFocused && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-purple-500/20 rounded-2xl blur-lg"
          />
        )}
      </AnimatePresence>

      {/* Input container */}
      <div
        className={`
          relative flex items-end gap-2 p-3 rounded-2xl
          bg-white dark:bg-slate-800/90 backdrop-blur-xl
          border-2 transition-all duration-200
          ${isFocused
            ? 'border-indigo-400 dark:border-indigo-500 shadow-lg'
            : 'border-slate-200 dark:border-slate-700 shadow-sm hover:border-slate-300 dark:hover:border-slate-600'
          }
        `}
      >
        {/* AI sparkle indicator */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute -top-2 -left-2 w-6 h-6 flex items-center justify-center bg-gradient-to-br from-indigo-500 to-violet-500 rounded-lg shadow-lg"
        >
          <Sparkles className="w-3.5 h-3.5 text-white" />
        </motion.div>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled || isLoading}
          placeholder={placeholder}
          rows={1}
          className={`
            flex-1 min-h-[44px] max-h-[150px] py-2.5 px-3
            bg-transparent resize-none
            text-slate-800 dark:text-slate-200 text-sm
            placeholder-slate-400 dark:placeholder-slate-500
            focus:outline-none
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
          style={{ lineHeight: '1.5' }}
        />

        {/* Action buttons */}
        <div className="flex items-center gap-1.5 flex-shrink-0 pb-0.5">
          {/* Send button */}
          <motion.button
            onClick={handleSubmit}
            disabled={!canSend}
            whileHover={canSend ? { scale: 1.05 } : {}}
            whileTap={canSend ? { scale: 0.95 } : {}}
            className={`
              p-2.5 rounded-xl transition-all duration-200
              ${canSend
                ? 'bg-gradient-to-r from-indigo-500 via-violet-500 to-purple-500 text-white shadow-lg hover:shadow-xl'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-not-allowed'
              }
            `}
          >
            <AnimatePresence mode="wait">
              {isLoading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0, rotate: -90 }}
                  animate={{ opacity: 1, rotate: 0 }}
                  exit={{ opacity: 0, rotate: 90 }}
                >
                  <Loader2 className="w-5 h-5 animate-spin" />
                </motion.div>
              ) : (
                <motion.div
                  key="send"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                >
                  <Send className="w-5 h-5" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        </div>
      </div>

      {/* Helper text */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mt-2 text-xs text-slate-400 dark:text-slate-500 text-center"
      >
        Press <kbd className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-slate-600 dark:text-slate-400 font-mono">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-slate-600 dark:text-slate-400 font-mono">Shift+Enter</kbd> for new line
      </motion.p>
    </motion.div>
  );
}

export default ChatInput;
