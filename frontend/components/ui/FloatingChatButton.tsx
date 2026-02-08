'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatInterface from '../chat/ChatInterface';
import { useAuth } from '../auth/AuthContext';

const FloatingChatButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const { user } = useAuth();

  // Animation variants for the chat panel
  const panelVariants = {
    hidden: {
      x: '100%',
      opacity: 0,
      scale: 0.9
    },
    visible: {
      x: 0,
      opacity: 1,
      scale: 1,
      transition: {
        type: 'spring',
        damping: 25,
        stiffness: 300,
        duration: 0.3
      }
    },
    exit: {
      x: '100%',
      opacity: 0,
      scale: 0.9,
      transition: {
        duration: 0.2
      }
    }
  };

  // Animation variants for the trigger button
  const buttonVariants = {
    initial: { scale: 1 },
    pulse: {
      scale: [1, 1.05, 1],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    }
  };

  // Effect to control the pulse animation
  useEffect(() => {
    if (!hasAnimated && !isOpen) {
      setHasAnimated(true);
    }
  }, [isOpen, hasAnimated]);

  // Close chat when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isOpen) {
        const chatPanel = document.getElementById('chat-panel');
        const chatButton = document.getElementById('floating-chat-button');

        if (chatPanel && !chatPanel.contains(event.target as Node) &&
            chatButton && !chatButton.contains(event.target as Node)) {
          setIsOpen(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  if (!user || !user.id) {
    // Don't show chat button if user is not authenticated
    return null;
  }

  return (
    <>
      {/* Floating Chat Button */}
      <motion.button
        id="floating-chat-button"
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-emerald-500 hover:bg-emerald-600 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
        variants={buttonVariants}
        initial="initial"
        animate={isOpen ? "initial" : "pulse"}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </motion.button>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            id="chat-panel"
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="fixed top-4 right-4 z-50 w-full max-w-md h-[calc(100vh-2rem)] max-h-[700px] bg-background border border-ui-border/20 rounded-2xl shadow-2xl overflow-hidden"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-ui-border/20">
                <h3 className="font-semibold text-foreground">AI Assistant</h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 rounded-full hover:bg-muted transition-colors"
                  aria-label="Close chat"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-muted-foreground"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              {/* Chat Interface */}
              <div className="flex-1 overflow-hidden p-2">
                <ChatInterface />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default FloatingChatButton;