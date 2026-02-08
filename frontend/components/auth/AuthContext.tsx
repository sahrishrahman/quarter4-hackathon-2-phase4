'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { isAuthenticated, getToken, getUserIdFromToken } from '@/lib/auth';

interface AuthContextType {
  user: {
    id: string | null;
    token: string | null;
  } | null;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<{ id: string | null; token: string | null } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatus = () => {
      const token = getToken();
      const userId = getUserIdFromToken();

      if (token && userId && isAuthenticated()) {
        setUser({
          id: userId,
          token: token
        });
      } else {
        setUser(null);
      }
    };

    // Initial check
    checkAuthStatus();
    setLoading(false);

    // Listen for storage changes (when login occurs from API calls)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'token') {
        // Add a small delay to ensure the token is written to localStorage before checking
        setTimeout(checkAuthStatus, 100);
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};