"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiGet } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Project } from "@/lib/types";
import { AppHeader } from "@/components/AppHeader";
import { BrandMark } from "@/components/BrandMark";

const STAGE_LABEL: Record<string, string> = { discovery: "Descubrimiento", validation: "Validación" };
const BUDGET_LABEL: Record<string, string> = { very_low: "muy bajo", low: "bajo", medium: "medio", high: "alto" };

export default function Dashboard() {
  const { authed, ready } = useAuth();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (ready && !authed) router.replace("/login");
  }, [authed, ready, router]);

  useEffect(() => {
    if (!authed) return;
    apiGet<Project[]>("/projects").then(setProjects).catch(() => {}).finally(() => setLoading(false));
  }, [authed]);

  return (
    <div className="min-h-screen">
      <AppHeader />
      <main id="contenido" className="mx-auto max-w-6xl px-5 py-10">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <span className="annot text-blueprint-600">Tus planos</span>
            <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">Proyectos</h1>
            <p className="mt-1 text-ink/60">Cada proyecto es una idea con su estrategia de validación.</p>
          </div>
          <Link href="/projects/new" className="btn-primary">
            <span className="text-base leading-none">＋</span> Nuevo proyecto
          </Link>
        </div>

        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[0, 1, 2].map((i) => <div key={i} className="card h-44 animate-pulse bg-line/40" />)}
          </div>
        ) : projects.length === 0 ? (
          <div className="card relative overflow-hidden px-6 py-20 text-center">
            <div className="bp-grid pointer-events-none absolute inset-0 opacity-60" />
            <div className="relative">
              <div className="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-blueprint-600 text-white">
                <BrandMark size={26} />
              </div>
              <h2 className="mt-5 font-display text-lg font-semibold text-ink">Aún no hay planos</h2>
              <p className="mx-auto mt-1.5 max-w-sm text-ink/60">
                Describe tu idea y deja que los agentes tracen su validación de principio a fin.
              </p>
              <Link href="/projects/new" className="btn-primary mt-6">Crear mi primer proyecto</Link>
            </div>
          </div>
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => {
              const isVal = p.constraints?.stage === "validation";
              return (
                <li key={p.id}>
                  <Link
                    href={`/projects/${p.id}`}
                    className="card group flex h-full flex-col p-5 transition hover:-translate-y-1 hover:shadow-lift focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blueprint-500 focus-visible:ring-offset-2"
                  >
                    <div className="mb-3 flex items-center justify-between">
                      <span
                        className={`badge ${isVal ? "bg-accent-500/15 text-accent-700" : "bg-blueprint-500/15 text-blueprint-700 dark:text-blueprint-300"}`}
                      >
                        <span className={`h-1.5 w-1.5 rounded-full ${isVal ? "bg-accent-500" : "bg-blueprint-500"}`} />
                        {STAGE_LABEL[p.constraints?.stage] ?? p.constraints?.stage}
                      </span>
                      <span className="text-line transition group-hover:translate-x-0.5 group-hover:text-blueprint-500">→</span>
                    </div>
                    <h2 className="font-display font-semibold text-ink">{p.name}</h2>
                    <p className="mt-1 line-clamp-3 flex-1 text-sm text-ink/60">{p.raw_idea}</p>
                    <div className="mt-4 border-t border-line pt-3">
                      <span className="annot">Presupuesto · {BUDGET_LABEL[p.constraints?.budget_level] ?? "—"}</span>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </main>
    </div>
  );
}
