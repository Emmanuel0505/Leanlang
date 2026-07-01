"use client";

import type { Report } from "@/lib/types";

export function ReportPanel({ report, onExport }: { report: Report; onExport?: (f: "md" | "json") => void }) {
  return (
    <div className="space-y-4">
      <div className="card relative overflow-hidden p-6">
        <div className="bp-grid pointer-events-none absolute inset-0 opacity-50" />
        <div className="relative">
          <span className="annot text-blueprint-600">Informe consolidado</span>
          <p className="mt-2 text-base leading-relaxed text-ink/85">{report.executive_summary}</p>
          {report.success_definition && (
            <div className="mt-4 rounded-xl border border-viab/30 bg-viab-soft/50 p-4">
              <div className="annot text-viab-ink">Validación exitosa si</div>
              <p className="mt-1 text-sm text-viab-ink">{report.success_definition}</p>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {report.riskiest_hypotheses?.length > 0 && (
          <div className="card p-5">
            <div className="mb-2 flex items-center gap-2">
              <span className="badge bg-accent-500 text-night">▲ probar primero</span>
            </div>
            <ul className="space-y-2 text-sm text-ink/75">
              {report.riskiest_hypotheses.map((h, i) => (
                <li key={i} className="flex gap-2"><span className="text-accent-700">•</span> {h}</li>
              ))}
            </ul>
          </div>
        )}
        {report.recommended_sequence?.length > 0 && (
          <div className="card p-5">
            <div className="annot mb-2">Secuencia recomendada</div>
            <ol className="space-y-2 text-sm text-ink/75">
              {report.recommended_sequence.map((e, i) => (
                <li key={i} className="flex gap-2.5">
                  <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-blueprint-600 font-mono text-[10px] font-semibold text-white">{i + 1}</span>
                  {e}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>

      {report.next_steps?.length > 0 && (
        <div className="card p-5">
          <div className="annot mb-3">Próximos pasos</div>
          <ul className="space-y-2">
            {report.next_steps.map((s, i) => (
              <li key={i} className="flex items-start gap-2.5 text-sm text-ink/80">
                <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-md bg-blueprint-500/15 text-blueprint-700 dark:text-blueprint-300">✓</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {onExport && (
        <div className="flex gap-2">
          <button onClick={() => onExport("md")} className="btn-secondary">Exportar informe .md</button>
          <button onClick={() => onExport("json")} className="btn-secondary">Exportar .json</button>
        </div>
      )}
    </div>
  );
}
