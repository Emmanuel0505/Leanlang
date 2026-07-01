"use client";

import type { ExperimentRec, ValidationRoadmap } from "@/lib/types";

/** Roadmap de validación por fases (Sequencing Agent): Descubrimiento → Validación. */
export function RoadmapView({ roadmap, recs }: { roadmap: ValidationRoadmap; recs: ExperimentRec[] }) {
  if (!roadmap.phases?.length) return null;
  const nameById = Object.fromEntries(recs.map((r) => [r.experiment_id, r.experiment_name]));

  return (
    <div className="card p-5">
      <div className="mb-1 flex items-center justify-between">
        <h3 className="font-display font-semibold text-ink">Roadmap de validación</h3>
        <span className="annot">{roadmap.phases.length} fases</span>
      </div>
      {roadmap.rationale && <p className="mb-4 text-sm text-ink/60">{roadmap.rationale}</p>}

      <ol className="space-y-3">
        {roadmap.phases.map((ph, i) => {
          const disc = ph.stage === "discovery";
          return (
            <li key={i} className="flex gap-4">
              <div className="flex flex-col items-center">
                <span className="grid h-8 w-8 place-items-center rounded-full bg-blueprint-600 font-mono text-sm font-semibold text-white">{i + 1}</span>
                {i < roadmap.phases.length - 1 && <span className="mt-1 w-px flex-1 bg-line" />}
              </div>
              <div className="flex-1 pb-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-display font-semibold text-ink">{ph.name}</span>
                  <span className={`badge ${disc ? "bg-blueprint-500/15 text-blueprint-700 dark:text-blueprint-300" : "bg-accent-500/15 text-accent-700"}`}>
                    {disc ? "Descubrimiento" : "Validación"}
                  </span>
                  {ph.duration_estimate && <span className="badge bg-paper text-ink/55">⏱ {ph.duration_estimate}</span>}
                </div>
                {ph.goal && <p className="mt-1 text-sm text-ink/65">{ph.goal}</p>}
                {ph.experiment_ids?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {ph.experiment_ids.map((id) => (
                      <span key={id} className="badge bg-paper text-ink/70">{nameById[id] ?? id}</span>
                    ))}
                  </div>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
