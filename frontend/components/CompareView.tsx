"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet } from "@/lib/api";
import type { Blueprint } from "@/lib/types";
import { BlueprintVersion } from "./VersionSelect";

interface Metrics {
  hyps: number; counter: number; riskiest: number; recs: number;
  disc: number; val: number; cards: number; score: number | null; passed?: boolean;
}

function metricsOf(bp: Blueprint): Metrics {
  const recs = bp.recommendations || [];
  return {
    hyps: bp.hypotheses?.length ?? 0,
    counter: (bp.hypotheses || []).filter((h) => h.is_counter_hypothesis).length,
    riskiest: (bp.prioritization || []).filter((p) => p.is_riskiest).length,
    recs: recs.length,
    disc: recs.filter((r) => r.stage === "discovery").length,
    val: recs.filter((r) => r.stage === "validation").length,
    cards: bp.test_cards?.length ?? 0,
    score: bp.critic_review ? Math.round((bp.critic_review.quality_score ?? 0) * 100) : null,
    passed: bp.critic_review?.passed,
  };
}

const expKey = (r: { hypothesis_id: string; experiment_id: string }) => `${r.hypothesis_id}:${r.experiment_id}`;

export function CompareView({
  versions, initialA, onClose,
}: {
  versions: BlueprintVersion[];
  initialA: string | null;
  onClose: () => void;
}) {
  const total = versions.length;
  const [aId, setAId] = useState(initialA ?? versions[0]?.id);
  const [bId, setBId] = useState(versions.find((v) => v.id !== (initialA ?? versions[0]?.id))?.id ?? versions[1]?.id);
  const [aBp, setABp] = useState<Blueprint | null>(null);
  const [bBp, setBBp] = useState<Blueprint | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancel = false;
    setLoading(true);
    Promise.all([
      apiGet<{ blueprint: Blueprint }>(`/blueprint/${aId}`),
      apiGet<{ blueprint: Blueprint }>(`/blueprint/${bId}`),
    ])
      .then(([a, b]) => { if (!cancel) { setABp(a.blueprint || {}); setBBp(b.blueprint || {}); } })
      .catch(() => { if (!cancel) { setABp({}); setBBp({}); } })
      .finally(() => { if (!cancel) setLoading(false); });
    return () => { cancel = true; };
  }, [aId, bId]);

  const label = (id: string) => {
    const i = versions.findIndex((v) => v.id === id);
    return `v${total - i}${i === 0 ? " · más reciente" : ""}`;
  };

  const ma = aBp ? metricsOf(aBp) : null;
  const mb = bBp ? metricsOf(bBp) : null;

  const expDiff = useMemo(() => {
    const sa = new Set((aBp?.recommendations || []).map(expKey));
    const sb = new Set((bBp?.recommendations || []).map(expKey));
    const added = [...sb].filter((k) => !sa.has(k));
    const removed = [...sa].filter((k) => !sb.has(k));
    return { added, removed };
  }, [aBp, bBp]);

  const ROWS: { label: string; get: (m: Metrics) => string; num?: (m: Metrics) => number }[] = [
    { label: "Hipótesis", get: (m) => `${m.hyps}`, num: (m) => m.hyps },
    { label: "Contra-hipótesis", get: (m) => `${m.counter}`, num: (m) => m.counter },
    { label: "Probar primero", get: (m) => `${m.riskiest}`, num: (m) => m.riskiest },
    { label: "Experimentos", get: (m) => `${m.recs}`, num: (m) => m.recs },
    { label: "· Descubrimiento", get: (m) => `${m.disc}`, num: (m) => m.disc },
    { label: "· Validación", get: (m) => `${m.val}`, num: (m) => m.val },
    { label: "Test Cards", get: (m) => `${m.cards}`, num: (m) => m.cards },
    { label: "Calidad", get: (m) => (m.score != null ? `${m.score}%` : "—"), num: (m) => m.score ?? 0 },
  ];

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display text-xl font-bold tracking-tight text-ink">Comparar versiones</h2>
        <button onClick={onClose} aria-label="Cerrar comparación" className="btn-ghost">
          <span aria-hidden="true">✕</span> Cerrar comparación
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Picker label="Versión A" value={aId} versions={versions} total={total} onChange={setAId} />
        <Picker label="Versión B" value={bId} versions={versions} total={total} onChange={setBId} />
      </div>

      {loading || !ma || !mb ? (
        <div className="card h-64 animate-pulse bg-line/40" />
      ) : (
        <>
          <div className="card overflow-x-auto">
            <table className="w-full min-w-[28rem] text-sm">
              <thead>
                <tr className="border-b border-line bg-paper/60 text-left">
                  <th className="px-4 py-2.5 font-medium text-ink/55">Métrica</th>
                  <th className="px-4 py-2.5 text-right font-mono text-blueprint-700">{label(aId)}</th>
                  <th className="px-4 py-2.5 text-right font-mono text-blueprint-700">{label(bId)}</th>
                  <th className="px-4 py-2.5 text-right font-medium text-ink/55">Δ</th>
                </tr>
              </thead>
              <tbody>
                {ROWS.map((r, i) => {
                  const va = r.num!(ma), vb = r.num!(mb);
                  const d = vb - va;
                  return (
                    <tr key={i} className="border-b border-line last:border-0">
                      <td className="px-4 py-2 text-ink/75">{r.label}</td>
                      <td className="px-4 py-2 text-right font-mono tabular-nums text-ink">{r.get(ma)}</td>
                      <td className="px-4 py-2 text-right font-mono tabular-nums text-ink">{r.get(mb)}</td>
                      <td className={`px-4 py-2 text-right font-mono tabular-nums ${d > 0 ? "text-viab-ink" : d < 0 ? "text-desire-ink" : "text-ink/40"}`}>
                        {d > 0 ? `+${d}` : d < 0 ? `${d}` : "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <DiffList title={`Solo en ${label(bId)}`} tone="viab" items={expDiff.added} />
            <DiffList title={`Solo en ${label(aId)}`} tone="desire" items={expDiff.removed} />
          </div>
        </>
      )}
    </div>
  );
}

function Picker({
  label, value, versions, total, onChange,
}: {
  label: string; value: string; versions: BlueprintVersion[]; total: number; onChange: (v: string) => void;
}) {
  return (
    <label className="card flex items-center justify-between gap-3 p-3">
      <span className="annot">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-line bg-surface px-2.5 py-1.5 text-sm text-ink focus:border-blueprint-400 focus:outline-none focus:ring-4 focus:ring-blueprint-500/10"
      >
        {versions.map((v, i) => (
          <option key={v.id} value={v.id}>v{total - i}{i === 0 ? " · más reciente" : ""}</option>
        ))}
      </select>
    </label>
  );
}

function DiffList({ title, tone, items }: { title: string; tone: "viab" | "desire"; items: string[] }) {
  const cls = tone === "viab" ? "bg-viab-soft text-viab-ink" : "bg-desire-soft text-desire-ink";
  return (
    <div className="card p-4">
      <div className="mb-2 flex items-center gap-2">
        <span className={`badge ${cls}`}>{items.length}</span>
        <span className="font-display text-sm font-semibold text-ink">{title}</span>
      </div>
      {items.length ? (
        <ul className="space-y-1">
          {items.map((k) => {
            const [hyp, exp] = k.split(":");
            return (
              <li key={k} className="flex items-center gap-2 text-sm text-ink/75">
                <span className="font-mono text-xs text-ink/50">{hyp}</span>
                <span>{exp}</span>
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="text-sm text-ink/50">Sin diferencias.</p>
      )}
    </div>
  );
}
