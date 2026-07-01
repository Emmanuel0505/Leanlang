"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getToken } from "@/lib/api";

/** Botones de llamada a la acción que se adaptan a si hay sesión activa. */
export function AuthCta({ variant = "hero" }: { variant?: "hero" | "nav" }) {
  const [authed, setAuthed] = useState<boolean | null>(null);
  useEffect(() => setAuthed(!!getToken()), []);

  if (variant === "nav") {
    if (authed === null) return <div className="h-9 w-24" />;
    return authed ? (
      <Link href="/dashboard" className="btn-primary h-9 px-4 py-0">
        Ir al panel
      </Link>
    ) : (
      <div className="flex items-center gap-2">
        <Link href="/login" className="btn-ghost h-9 px-3 py-0">
          Entrar
        </Link>
        <Link href="/register" className="btn-primary h-9 px-4 py-0">
          Empezar gratis
        </Link>
      </div>
    );
  }

  // hero
  if (authed === null) return <div className="h-12" />;
  return (
    <div className="flex flex-col gap-3 sm:flex-row">
      {authed ? (
        <Link href="/dashboard" className="btn-primary px-6 py-3 text-base">
          Ir a mi panel →
        </Link>
      ) : (
        <>
          <Link href="/register" className="btn-primary px-6 py-3 text-base shadow-glow">
            Trazar mi blueprint →
          </Link>
          <Link href="/login" className="btn-secondary px-6 py-3 text-base">
            Ya tengo cuenta
          </Link>
        </>
      )}
    </div>
  );
}
