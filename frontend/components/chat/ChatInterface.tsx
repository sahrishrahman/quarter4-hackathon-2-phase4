'use client';

import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';
import { useAuth } from '@/components/auth/AuthContext';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatInterfaceProps {
  initialMessages?: Message[];
}

interface TaskOperation {
  tool: string;
  result?: {
    id?: string;
    title?: string;
    email?: string;
    error?: string;
  };
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ initialMessages = [] }) => {
  const [inputValue, setInputValue] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const { user } = useAuth(); // Get user from auth context

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) {
      // Show error for empty message
      const errorFeedback: Message = {
        id: `error-${Date.now()}`,
        content: 'Please enter a message.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorFeedback]);
      return;
    }

    if (!user?.id) {
      // Show error for unauthenticated user
      const errorFeedback: Message = {
        id: `error-${Date.now()}`,
        content: 'You must be logged in to use the chatbot. Please sign in first.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorFeedback]);
      return;
    }

    if (isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    // Add user message to the chat
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send message to backend
      console.log("conversationId", conversationId)
      const response = await sendChatMessage(user.id, inputValue, conversationId ?? undefined);

      // Update conversation ID if it's the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant message to the chat
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        content: response.message,
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Handle any task operations if returned
      if (response.task_operations && response.task_operations.length > 0) {
        console.log('Task operations:', response.task_operations);

        // Show feedback for task operations
        response.task_operations.forEach((operation: TaskOperation) => {
          if (operation.result && operation.result.error) {
            // Add error message to the chat
            const errorFeedback: Message = {
              id: `feedback-${Date.now()}-${Math.random()}`,
              content: `⚠️ ${operation.result.error}`,
              role: 'assistant',
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorFeedback]);
          } else if (operation.tool === 'add_task' && operation.result?.id) {
            // Add success message for task creation
            const successMessage: Message = {
              id: `feedback-${Date.now()}-${Math.random()}`,
              content: `✅ Added task "${operation.result.title}" to your list.`,
              role: 'assistant',
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, successMessage]);
          } else if (operation.tool === 'get_current_user' && operation.result?.email) {
            // Add identity confirmation message
            const identityMessage: Message = {
              id: `feedback-${Date.now()}-${Math.random()}`,
              content: `👤 You are logged in as ${operation.result.email}.`,
              role: 'assistant',
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, identityMessage]);
          }
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to the chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-background rounded-2xl border border-ui-border/20 shadow-lg">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[500px]">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-4">
            <div className="text-muted-foreground mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-foreground mb-2">Welcome to Your AI Assistant!</h3>
            <p className="text-muted-foreground max-w-md">
              I'm here to help you manage your tasks using natural language. Try saying things like:
            </p>
            <ul className="mt-3 text-left text-sm text-muted-foreground space-y-1">
              <li>• "Add a task to buy groceries tomorrow"</li>
              <li>• "Show me my tasks"</li>
              <li>• "Mark 'buy groceries' as complete"</li>
              <li>• "Delete the meeting prep task"</li>
            </ul>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground rounded-br-none'
                    : 'bg-muted text-foreground rounded-bl-none'
                }`}
              >
                <div className="whitespace-pre-wrap break-words">{message.content}</div>
                <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted text-foreground rounded-2xl rounded-bl-none px-4 py-3 max-w-[80%]">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-ui-border/20 p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message here..."
            className="flex-1 min-h-[60px] max-h-32 px-4 py-3 bg-muted border border-ui-border/20 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-primary/30"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !user?.id || !inputValue.trim()}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity whitespace-nowrap"
          >
            {user?.id ? 'Send' : 'Sign In Required'}
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Ask me to add, list, update, or delete tasks using natural language
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;