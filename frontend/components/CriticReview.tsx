import type { CriticReview } from "@/lib/types";
import { StatusBadge, StatusDot, qualityStatus, type Status } from "./Status";

const SEV: Record<string, { status: Status; label: string }> = {
  high: { status: "danger", label: "alta" },
  medium: { status: "warn", label: "media" },
  low: { status: "neutral", label: "baja" },
};

const BAR: Record<Status, string> = { ok: "bg-ok", warn: "bg-warn", danger: "bg-danger", neutral: "bg-ink/30" };

export function CriticReviewView({ review }: { review: CriticReview }) {
  const pct = Math.round((review.quality_score ?? 0) * 100);
  const status = qualityStatus(review.quality_score ?? 0);

  return (
    <div className="card p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h3 className="font-display font-semibold text-ink">Revisión del coach</h3>
        <StatusBadge status={status} className="px-3 py-1 text-sm font-semibold">
          {review.passed ? "Aprobado" : "Requiere mejoras"} · {pct}%
        </StatusBadge>
      </div>

      <div className="mb-1 flex items-center justify-between">
        <span className="annot">Calidad del diseño</span>
        <span className="data">{pct}/100</span>
      </div>
      <div className="mb-4 h-2 overflow-hidden rounded-full bg-line/70">
        <div className={`h-full rounded-full ${BAR[status]}`} style={{ width: `${pct}%` }} />
      </div>

      <p className="mb-4 text-sm leading-relaxed text-ink/70">{review.summary}</p>

      {review.issues.length > 0 && (
        <ul className="space-y-2">
          {review.issues.map((it, i) => {
            const sev = SEV[it.severity] || SEV.low;
            return (
              <li key={i} className="rounded-xl border border-line bg-paper/50 p-3 text-sm">
                <div className="flex items-center gap-2">
                  <StatusBadge status={sev.status}>severidad {sev.label}</StatusBadge>
                  <span className="font-display font-medium text-ink">{it.pitfall}</span>
                </div>
                <p className="mt-1.5 text-ink/70">{it.detail}</p>
                <p className="mt-1 text-ink/60">
                  <span className="font-medium text-blueprint-700">→ </span>{it.suggestion}
                </p>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
