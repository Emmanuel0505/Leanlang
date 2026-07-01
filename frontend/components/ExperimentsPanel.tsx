"use client";

import { useMemo } from "react";
import type { ExperimentRec, PlanEstimate, ValidationRoadmap } from "@/lib/types";
import { ExperimentSequence } from "./ExperimentSequence";
import { RoadmapView } from "./RoadmapView";
import { PlanEstimateCard } from "./PlanEstimateCard";
import { HypFilter } from "./HypFilter";

export function ExperimentsPanel({
  recs,
  roadmap,
  estimate,
  focusHyp,
  onFocus,
}: {
  recs: ExperimentRec[];
  roadmap?: ValidationRoadmap;
  estimate?: PlanEstimate;
  focusHyp: string | null;
  onFocus: (v: string | null) => void;
}) {
  const ids = useMemo(() => Array.from(new Set(recs.map((r) => r.hypothesis_id))).sort(), [recs]);
  const filtered = focusHyp ? recs.filter((r) => r.hypothesis_id === focusHyp) : recs;
  const discovery = filtered.filter((r) => r.stage === "discovery");
  const validation = filtered.filter((r) => r.stage === "validation");

  return (
    <div className="space-y-5">
      {estimate && !focusHyp && <PlanEstimateCard est={estimate} />}
      {roadmap && !focusHyp && <RoadmapView roadmap={roadmap} recs={recs} />}

      <HypFilter ids={ids} value={focusHyp} onChange={onFocus} />

      <p className="rounded-xl border border-line bg-paper/60 px-4 py-2.5 text-sm text-ink/65">
        Secuencia recomendada: empieza por <strong className="font-semibold text-blueprint-700">Descubrimiento</strong>{" "}
        (barato y rápido) y avanza a <strong className="font-semibold text-accent-700">Validación</strong> conforme crece la certeza.
      </p>

      <Group title="Descubrimiento" tone="blueprint" recs={discovery} />
      <Group title="Validación" tone="amber" recs={validation} />
    </div>
  );
}

function Group({ title, tone, recs }: { title: string; tone: "blueprint" | "amber"; recs: ExperimentRec[] }) {
  if (!recs.length) return null;
  const dot = tone === "blueprint" ? "bg-blueprint-500" : "bg-accent-500";
  return (
    <section>
      <div className="mb-3 flex items-center gap-2">
        <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
        <h3 className="font-display text-base font-semibold text-ink">{title}</h3>
        <span className="badge bg-paper font-mono text-ink/55">{recs.length}</span>
      </div>
      <ExperimentSequence recs={recs} />
    </section>
  );
}
