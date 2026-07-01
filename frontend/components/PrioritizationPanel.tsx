"use client";

import { useEffect, useState } from "react";
import type { Hypothesis, Prioritization, Quadrant } from "@/lib/types";
import { AssumptionsMap2x2 } from "./AssumptionsMap2x2";

function quadrantOf(importance: number, evidence: number): Quadrant {
  if (importance >= 0.5) return evidence < 0.5 ? "test_now" : "keep_evidence";
  return evidence < 0.5 ? "deprioritize" : "park";
}

export function PrioritizationPanel({
  items,
  hypotheses,
  editable,
  onConfirm,
}: {
  items: Prioritization[];
  hypotheses: Hypothesis[];
  editable: boolean;
  onConfirm: (edited: Prioritization[]) => void;
}) {
  const [edited, setEdited] = useState<Prioritization[]>(items);
  const [touched, setTouched] = useState(false);
  useEffect(() => { setEdited(items); setTouched(false); }, [items]);

  const view = editable ? edited : items;
  const hMap = Object.fromEntries(hypotheses.map((h) => [h.id, h.statement]));
  const riskiest = view.filter((p) => p.is_riskiest);

  function handleMove(id: string, importance: number, evidence: number) {
    setTouched(true);
    setEdited((prev) =>
      prev.map((p) =>
        p.hypothesis_id === id
          ? { ...p, importance, evidence, is_riskiest: importance >= 0.5 && evidence < 0.5, quadrant: quadrantOf(importance, evidence) }
          : p,
      ),
    );
  }

  return (
    <div className="space-y-4">
      <AssumptionsMap2x2 items={view} editable={editable} onMove={handleMove} />

      <div className="card p-5">
        <div className="mb-3 flex items-center gap-2">
          <span className="badge bg-accent-500 text-ink">▲ probar primero</span>
          <span className="annot">{riskiest.length} de {view.length} hipótesis</span>
        </div>
        {riskiest.length ? (
          <ol className="space-y-2">
            {riskiest.map((p) => (
              <li key={p.hypothesis_id} className="flex gap-2 text-sm">
                <span className="font-mono text-xs font-semibold text-accent-700">{p.hypothesis_id}</span>
                <span className="text-ink/75">{hMap[p.hypothesis_id]}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-sm text-ink/55">Ningún supuesto cae en el cuadrante de probar primero.</p>
        )}
      </div>

      {editable && (
        <div className="flex flex-wrap items-center gap-3">
          <button onClick={() => onConfirm(edited)} className="btn-amber">
            Confirmar priorización y seleccionar experimentos →
          </button>
          {touched && (
            <button onClick={() => { setEdited(items); setTouched(false); }} className="btn-ghost">
              Descartar ajustes
            </button>
          )}
          <span className="annot">{touched ? "Con ajustes manuales" : "Sin cambios"}</span>
        </div>
      )}
    </div>
  );
}
