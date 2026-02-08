"use client";

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { TodoCard } from '@/components/todo/TodoCard';
import type { Todo } from '@/lib/types';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { EmptyState } from '@/components/ui/EmptyState';
import { useToast } from '@/components/ui/Toast';
import { cn } from '@/lib/utils';
import { getTodos, createTodo, updateTodo, deleteTodo, toggleTodoComplete } from '@/lib/api';
import { Plus, Sparkles, Layout, CheckCircle2, ListTodo, Calendar, Clock, ArrowRight, X } from 'lucide-react';
import Hero from '@/components/layout/Hero';

export default function DashboardPage() {
  const [todos, setTodos] = React.useState<Todo[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [showAddModal, setShowAddModal] = React.useState(false);
  const [editingTodo, setEditingTodo] = React.useState<Todo | null>(null);
  const [formData, setFormData] = React.useState({ title: '', description: '' });
  const [userName, setUserName] = React.useState('');
  const router = useRouter();
  const { addToast } = useToast();

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const name = localStorage.getItem('user_name');
      if (name) setUserName(name);
    }

    const fetchTodos = async () => {
      try {
        setLoading(true);
        const data = await getTodos();
        setTodos(data);
      } catch (error) {
        console.error('Failed to fetch todos:', error);
        addToast({
          type: 'error',
          message: 'Failed to load tasks',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchTodos();
  }, [addToast]);

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    try {
      const newTodo = await createTodo({
        title: formData.title,
        description: formData.description,
        completed: false,
      });
      setTodos([newTodo, ...todos]);
      setShowAddModal(false);
      setFormData({ title: '', description: '' });
      addToast({
        type: 'success',
        message: 'Task created successfully!',
        duration: 3000,
      });
    } catch (error) {
      console.error('Failed to create todo:', error);
      addToast({
        type: 'error',
        message: 'Failed to create task',
      });
    }
  };

  const handleEditTodo = (todo: Todo) => {
    setEditingTodo(todo);
    setFormData({ title: todo.title, description: todo.description || '' });
  };

  const handleUpdateTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTodo || !formData.title.trim()) return;

    try {
      const updated = await updateTodo(editingTodo.id, {
        title: formData.title,
        description: formData.description,
        completed: editingTodo.completed,
      });
      setTodos(todos.map((todo) => (todo.id === updated.id ? updated : todo)));
      setEditingTodo(null);
      setFormData({ title: '', description: '' });
      addToast({
        type: 'success',
        message: 'Task updated successfully',
        duration: 3000,
      });
    } catch (error) {
      console.error('Failed to update todo:', error);
      addToast({
        type: 'error',
        message: 'Failed to update task',
      });
    }
  };

  const handleToggleTodo = async (id: number) => {
    const todo = todos.find((t) => t.id === id);
    if (!todo) return;

    try {
      const updated = await toggleTodoComplete(id, !todo.completed);
      setTodos(todos.map((t) => (t.id === id ? updated : t)));

      if (updated.completed) {
        addToast({
          type: 'success',
          message: '🎉 Task completed! Great job!',
          duration: 3000,
        });
      }
    } catch (error) {
      console.error('Failed to toggle todo:', error);
      addToast({
        type: 'error',
        message: 'Failed to update task',
      });
    }
  };

  const handleDeleteTodo = async (id: number) => {
    try {
      await deleteTodo(id);
      setTodos(todos.filter((todo) => todo.id !== id));
      addToast({
        type: 'info',
        message: 'Task deleted',
        duration: 3000,
      });
    } catch (error) {
      console.error('Failed to delete todo:', error);
      addToast({
        type: 'error',
        message: 'Failed to delete task',
      });
    }
  };

  const completedCount = todos.filter((t) => t.completed).length;
  const totalCount = todos.length;
  const progress = totalCount === 0 ? 0 : Math.round((completedCount / totalCount) * 100);

  return (
    <div className="min-h-[calc(100vh-80px)] bg-background">
      <div className="section-horizontal section-vertical max-w-7xl mx-auto">
        {/* Hero */}
        <div className="animate-welcome">
          <React.Suspense fallback={<div className="h-36" />}> 
            {/* lazy-like boundary for hero */}
            {/* @ts-ignore - dynamic import not necessary */}
            <Hero userName={userName || 'User'} pending={totalCount - completedCount} onPrimaryAction={() => setShowAddModal(true)} />
          </React.Suspense>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-16 animate-welcome" style={{ animationDelay: '0.1s' }}>
          <div className="lg:col-span-3 glass-premium p-10 rounded-[3rem] relative overflow-hidden group border-white/10">
            <div className="absolute top-0 right-0 p-10 opacity-[0.03] group-hover:opacity-[0.07] transition-opacity duration-1000">
              <Layout className="w-64 h-64 -mr-16 -mt-16 rotate-12" />
            </div>
            <div className="relative z-10">
              <div className="flex justify-between items-end mb-8">
                <div>
                  <p className="text-xs font-black opacity-40 uppercase tracking-[0.3em] mb-3">Productivity Pulse</p>
                  <div className="flex items-center gap-4">
                    <span className="text-7xl font-black tracking-tighter text-foreground">{progress}%</span>
                    <div className="px-4 py-2 bg-emerald-500/10 text-emerald-500 rounded-full text-xs font-black border border-emerald-500/20">
                      +12% INCREMENTAL
                    </div>
                  </div>
                </div>
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-bold opacity-60">Success Rate</p>
                  <p className="text-2xl font-black text-primary">{completedCount}/{totalCount}</p>
                </div>
              </div>
              <div className="w-full h-3 bg-muted/30 rounded-full overflow-hidden mb-6 border border-ui-border/10 p-0.5">
                <div
                  className="h-full bg-gradient-to-r from-primary via-purple-500 to-indigo-500 rounded-full transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(var(--primary),0.5)]"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm opacity-60 font-bold max-w-md">
                {totalCount === 0
                  ? "System initialized. Waiting for task deployment."
                  : `Masterfully executed ${completedCount} objectives. ${totalCount - completedCount} remaining for peak performance.`}
              </p>
            </div>
          </div>

          <div className="glass-premium p-10 rounded-[3rem] flex flex-col justify-between border-white/10 hover:border-primary/40 transition-all duration-500 group cursor-pointer" onClick={() => setShowAddModal(true)}>
            <div>
              <div className="w-16 h-16 rounded-[1.5rem] bg-foreground text-background flex items-center justify-center mb-8 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 shadow-xl shadow-foreground/20">
                <Plus className="w-8 h-8" strokeWidth={3} />
              </div>
              <h3 className="text-2xl font-black tracking-tight mb-2">New Entry</h3>
              <p className="text-sm opacity-60 font-bold leading-relaxed">Instantly capture high-priority tasks in your daily routine.</p>
            </div>
            <div className="mt-8 flex items-center gap-2 text-primary text-sm font-black uppercase tracking-widest group-hover:translate-x-2 transition-transform">
              Initialize <ArrowRight className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* Tasks Section Header */}
        <div className="flex items-center justify-between mb-10 animate-welcome" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center gap-4">
            <h3 className="text-2xl font-black tracking-tighter">Current Objectives</h3>
            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            <span className="px-4 py-1 bg-muted/50 rounded-full text-foreground text-[10px] font-black tracking-[0.2em] border border-ui-border/20">
              {todos.length} REGISTRY
            </span>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {Array.from({ length: 6 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && todos.length === 0 && (
          <div className="animate-welcome" style={{ animationDelay: '0.3s' }}>
            <EmptyState
              type="no-todos"
              title="Registry Clear"
              description="No active tasks detected. Ready for new system entry."
              cta={{
                text: 'Deploy First Task',
                action: () => setShowAddModal(true),
              }}
            />
          </div>
        )}

        {/* Todo List Grid */}
        {!loading && todos.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {todos.map((todo, index) => (
              <div
                key={todo.id}
                className="animate-welcome"
                style={{ animationDelay: `${0.3 + index * 0.05}s` }}
              >
                <TodoCard
                  todo={todo}
                  onToggle={handleToggleTodo}
                  onDelete={handleDeleteTodo}
                  onEdit={handleEditTodo}
                  index={index}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal - Common Style for Add and Edit */}
      {(showAddModal || editingTodo) && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-6 sm:p-4">
          <div
            className="absolute inset-0 bg-background/90 backdrop-blur-2xl animate-in fade-in duration-500"
            onClick={() => {
              setShowAddModal(false);
              setEditingTodo(null);
              setFormData({ title: '', description: '' });
            }}
          />
          <div className="relative glass-premium w-full max-w-xl rounded-[3.5rem] p-10 md:p-14 border border-white/20 shadow-[0_50px_100px_rgba(0,0,0,0.4)] animate-in zoom-in-95 duration-500">
            <div className="flex items-center justify-between mb-12">
              <div className="flex items-center gap-5">
                <div className="w-14 h-14 rounded-2xl bg-primary text-white flex items-center justify-center shadow-2xl shadow-primary/30">
                  {editingTodo ? <Sparkles className="w-7 h-7" /> : <Plus className="w-7 h-7" />}
                </div>
                <div>
                  <h3 className="text-3xl font-black tracking-tight leading-none mb-1">
                    {editingTodo ? 'Edit Task' : 'New Task'}
                  </h3>
                  <p className="text-xs uppercase font-black opacity-40 tracking-widest">System Update Protocol</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowAddModal(false);
                  setEditingTodo(null);
                  setFormData({ title: '', description: '' });
                }}
                className="w-12 h-12 rounded-2xl hover:bg-muted transition-all duration-300 flex items-center justify-center group active:scale-90"
              >
                <X className="w-6 h-6 text-muted-foreground group-hover:text-foreground transition-colors" />
              </button>
            </div>

            <form onSubmit={editingTodo ? handleUpdateTodo : handleAddTodo} className="space-y-8">
              <div className="space-y-3">
                <label className="text-[10px] font-black opacity-40 uppercase tracking-[0.4em] pl-1">Objective Title</label>
                <Input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Task identification..."
                  autoFocus
                  required
                  className="h-16 rounded-2xl bg-muted/30 text-xl border-2 border-transparent focus:border-primary/50 transition-all shadow-inner font-bold"
                />
              </div>

              <div className="space-y-3">
                <label className="text-[10px] font-black opacity-40 uppercase tracking-[0.4em] pl-1">Functional Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Additional parameters (optional)..."
                  rows={4}
                  className="w-full rounded-2xl px-6 py-5 bg-muted/30 text-lg border-2 border-transparent focus:border-primary/50 transition-all resize-none outline-none shadow-inner font-medium placeholder:opacity-50"
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-4 pt-6">
                <Button
                  type="button"
                  variant="secondary"
                  fullWidth
                  onClick={() => {
                    setShowAddModal(false);
                    setEditingTodo(null);
                    setFormData({ title: '', description: '' });
                  }}
                  className="h-16 rounded-[1.75rem] font-black text-sm uppercase tracking-widest border-ui-border/20 glass-premium"
                >
                  Discard
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  fullWidth
                  className="h-16 rounded-[1.75rem] font-black text-sm uppercase tracking-widest shadow-[0_20px_40px_rgba(var(--primary),0.3)] group"
                >
                  {editingTodo ? 'Deploy Update' : 'Initialize Task'}
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
