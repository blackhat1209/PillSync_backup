import React, { createContext, useContext, useEffect, useState } from 'react';
import { currentUser, login, logout, register } from '../features/auth/authService';
import { getAccessToken } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('pillsync_user') || 'null'); } catch (_) { return null; }
  });
  const [loading, setLoading] = useState(Boolean(getAccessToken()));

  useEffect(() => {
    if (!getAccessToken()) { setLoading(false); return; }
    currentUser().then(setUser).catch(() => { logout(); setUser(null); }).finally(() => setLoading(false));
  }, []);

  const value = {
    user,
    loading,
    login: async (username, password) => { const u = await login(username, password); setUser(u); return u; },
    register: async (payload) => { const u = await register(payload); setUser(u); return u; },
    logout: () => { logout(); setUser(null); },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
