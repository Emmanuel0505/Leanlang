"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { clearToken, getToken, login as apiLogin, register as apiRegister, setToken } from "./api";

const EMAIL_KEY = "vb_email";

interface AuthCtx {
  authed: boolean;
  ready: boolean;
  email: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const Ctx = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authed, setAuthed] = useState(false);
  const [ready, setReady] = useState(false);
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    setAuthed(!!getToken());
    try { setEmail(localStorage.getItem(EMAIL_KEY)); } catch { /* noop */ }
    setReady(true);
  }, []);

  function remember(addr: string) {
    setEmail(addr);
    try { localStorage.setItem(EMAIL_KEY, addr); } catch { /* noop */ }
  }

  async function login(addr: string, password: string) {
    const token = await apiLogin(addr, password);
    setToken(token);
    setAuthed(true);
    remember(addr);
  }

  async function register(addr: string, password: string) {
    await apiRegister(addr, password);
    await login(addr, password);
  }

  function logout() {
    clearToken();
    try { localStorage.removeItem(EMAIL_KEY); } catch { /* noop */ }
    setAuthed(false);
    setEmail(null);
  }

  return <Ctx.Provider value={{ authed, ready, email, login, register, logout }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth fuera de AuthProvider");
  return ctx;
}
