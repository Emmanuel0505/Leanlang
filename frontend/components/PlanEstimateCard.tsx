"use client";

import type { PlanEstimate } from "@/lib/types";
import { StatusBadge } from "./Status";

/** Estimación de costo/esfuerzo/capacidades del plan (Plan Estimation Agent). */
export function PlanEstimateCard({ est }: { est: PlanEstimate }) {
  const ok = est.within_budget && est.within_time;
  return (
    <div className="card p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-display font-semibold text-ink">Estimación del plan</h3>
        <StatusBadge status={ok ? "ok" : "danger"}>
          {ok ? "Dentro de tus restricciones" : "Excede tus restricciones"}
        </StatusBadge>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <Metric label="Experimentos" value={est.experiment_count} />
        <Metric label="Costo (pts)" value={est.total_cost_points} sub={`máx ${est.max_cost}/5`} status={est.within_budget ? "ok" : "danger"} />
        <Metric label="Esfuerzo (pts)" value={est.total_effort_points} sub="setup + ejecución" status={est.within_time ? "ok" : "warn"} />
      </div>

      {est.required_capabilities.length > 0 && (
        <div className="mt-4">
          <div className="annot mb-1.5">Capacidades necesarias</div>
          <div className="flex flex-wrap gap-1.5">
            {est.required_capabilities.map((c) => <span key={c} className="badge bg-paper text-ink/70">{c}</span>)}
          </div>
        </div>
      )}

      {est.warnings.length > 0 && (
        <ul className="mt-4 space-y-1.5">
          {est.warnings.map((w, i) => (
            <li key={i} className="flex items-start gap-2 rounded-lg bg-danger-soft/60 px-3 py-2 text-sm text-danger-ink">
              <span aria-hidden>⚠</span> {w}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function Metric({ label, value, sub, status }: { label: string; value: number; sub?: string; status?: "ok" | "warn" | "danger" }) {
  const color = status === "danger" ? "text-danger-ink" : status === "warn" ? "text-warn-ink" : "text-ink";
  return (
    <div className="rounded-xl border border-line bg-paper/50 p-3 text-center">
      <div className={`font-display text-2xl font-bold ${color}`}>{value}</div>
      <div className="annot mt-0.5">{label}</div>
      {sub && <div className="mt-0.5 text-[11px] text-ink/45">{sub}</div>}
    </div>
  );
}
