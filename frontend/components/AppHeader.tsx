"use client";

import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";
import { UserMenu } from "./UserMenu";

/** Barra superior de las páginas autenticadas. */
export function AppHeader() {
  return (
    <header className="glass sticky top-0 z-30 border-b">
      <a
        href="#contenido"
        className="sr-only rounded-lg bg-blueprint-600 px-4 py-2 text-sm font-semibold text-white focus:not-sr-only focus:absolute focus:left-4 focus:top-2.5 focus:z-50"
      >
        Saltar al contenido
      </a>
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-5">
        <Logo href="/dashboard" />
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
