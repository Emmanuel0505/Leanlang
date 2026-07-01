import type { RiskLevel } from "@/lib/types";

export type Status = "ok" | "warn" | "danger" | "neutral";

const DOT: Record<Status, string> = {
  ok: "bg-ok",
  warn: "bg-warn",
  danger: "bg-danger",
  neutral: "bg-ink/30",
};

const CHIP: Record<Status, string> = {
  ok: "bg-ok-soft text-ok-ink",
  warn: "bg-warn-soft text-warn-ink",
  danger: "bg-danger-soft text-danger-ink",
  neutral: "bg-paper text-ink/60",
};

/** Punto de semáforo (verde / ámbar / rojo). */
export function StatusDot({ status, pulse = false, className = "" }: { status: Status; pulse?: boolean; className?: string }) {
  return <span aria-hidden className={`inline-block h-2.5 w-2.5 shrink-0 rounded-full ${DOT[status]} ${pulse ? "anim-pulse2" : ""} ${className}`} />;
}

/** Badge de estado con punto + texto. */
export function StatusBadge({ status, children, className = "" }: { status: Status; children: React.ReactNode; className?: string }) {
  return (
    <span className={`badge ${CHIP[status]} ${className}`}>
      <StatusDot status={status} />
      {children}
    </span>
  );
}

// ── Mapeos de dominio → estado (umbrales centralizados) ──────────────────────
export function riskLevelStatus(level?: RiskLevel | string): Status {
  if (level === "high") return "danger";
  if (level === "low") return "ok";
  if (level === "medium") return "warn";
  return "neutral";
}

const RISK_LABEL: Record<string, string> = { high: "Riesgo alto", medium: "Riesgo medio", low: "Riesgo bajo" };

/** Semáforo de nivel de riesgo de una hipótesis (high/medium/low). */
export function RiskLevelBadge({ level }: { level?: RiskLevel | string }) {
  if (!level) return null;
  return <StatusBadge status={riskLevelStatus(level)}>{RISK_LABEL[level] ?? level}</StatusBadge>;
}

/** Calidad del diseño (0–1): ≥0.7 verde · ≥0.5 ámbar · resto rojo. */
export function qualityStatus(score: number): Status {
  if (score >= 0.7) return "ok";
  if (score >= 0.5) return "warn";
  return "danger";
}

/** Fuerza de evidencia (1–5): ≥4 verde · 3 ámbar · ≤2 rojo. */
export function evidenceStatus(strength: number): Status {
  if (strength >= 4) return "ok";
  if (strength === 3) return "warn";
  return "danger";
}
