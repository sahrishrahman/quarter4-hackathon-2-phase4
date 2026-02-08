'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import ChatInterface from '@/components/chat/ChatInterface';
import { useAuth } from '@/components/auth/AuthContext';
import { ArrowLeft } from 'lucide-react';

const ChatPage: React.FC = () => {
  const router = useRouter();
  const { user, loading } = useAuth();

  // If still loading auth, show loading state
  if (loading) {
    return (
      <div className="min-h-[calc(100vh-80px)] flex items-center justify-center">
        <div className="text-lg text-muted-foreground">Loading...</div>
      </div>
    );
  }

  // If not authenticated, redirect to sign-in
  if (!user) {
    router.push('/auth/sign-in');
    return null;
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-background py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <h1 className="text-2xl font-black">AI Task Assistant</h1>
          </div>
          <div className="text-sm text-muted-foreground">
            Hello, {user.name || user.email || 'User'}!
          </div>
        </div>

        {/* Chat Container */}
        <div className="bg-background border border-ui-border/20 rounded-2xl shadow-xl overflow-hidden">
          <div className="p-6 border-b border-ui-border/20">
            <h2 className="text-xl font-bold text-foreground">Manage Your Tasks with AI</h2>
            <p className="text-muted-foreground mt-1">
              Use natural language to add, list, update, and complete your tasks
            </p>
          </div>

          <div className="p-4 h-[600px] flex flex-col">
            <ChatInterface />
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-premium rounded-2xl p-5 border border-white/10">
            <h3 className="font-bold text-foreground mb-2">Examples</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• "Add a task to buy groceries tomorrow"</li>
              <li>• "Show me my tasks"</li>
              <li>• "Mark 'buy groceries' as complete"</li>
            </ul>
          </div>
          <div className="glass-premium rounded-2xl p-5 border border-white/10">
            <h3 className="font-bold text-foreground mb-2">Tips</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Be specific with dates and times</li>
              <li>• Refer to tasks by name</li>
              <li>• Ask for lists of pending or completed tasks</li>
            </ul>
          </div>
          <div className="glass-premium rounded-2xl p-5 border border-white/10">
            <h3 className="font-bold text-foreground mb-2">Capabilities</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Create tasks with due dates</li>
              <li>• List, update, and delete tasks</li>
              <li>• Mark tasks as complete</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;