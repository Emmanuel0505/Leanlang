"use client";

export interface NavStage {
  key: string;
  label: string;
  n?: number;
}

interface Props {
  stages: NavStage[];
  activeKey: string;
  readySet: Set<string>;
  doneSet: Set<string>;
  gateKey: string | null;
  runningKey: string | null;
  onSelect: (key: string) => void;
}

/** Navegador de estaciones del blueprint: el progreso ES la navegación (esquema técnico). */
export function BlueprintNav({ stages, activeKey, readySet, doneSet, gateKey, runningKey, onSelect }: Props) {
  return (
    <nav aria-label="Estaciones del blueprint">
      {/* Vertical (≥ lg) */}
      <ol className="hidden lg:block">
        {stages.map((s, i) => {
          const ready = readySet.has(s.key);
          const done = doneSet.has(s.key);
          const isGate = gateKey === s.key;
          const isRunning = runningKey === s.key;
          const active = activeKey === s.key;
          const last = i === stages.length - 1;
          return (
            <li key={s.key} className="relative pl-9">
              {/* conector */}
              {!last && (
                <span className={`absolute left-[14px] top-7 h-[calc(100%-12px)] w-px ${done ? "bg-blueprint-300" : "bg-line"}`} />
              )}
              {/* nodo */}
              <span
                className={`absolute left-0 top-1.5 grid h-7 w-7 place-items-center rounded-full border-2 font-mono text-[11px] font-semibold transition ${
                  isGate
                    ? "border-accent-500 bg-accent-500 text-ink shadow-amber anim-pulse2"
                    : done
                    ? "border-blueprint-600 bg-blueprint-600 text-white"
                    : isRunning
                    ? "border-blueprint-500 bg-surface text-blueprint-600 dark:text-blueprint-300 anim-pulse2"
                    : active
                    ? "border-blueprint-500 bg-surface text-blueprint-600 dark:text-blueprint-300"
                    : ready
                    ? "border-line bg-surface text-ink/50"
                    : "border-line bg-paper text-ink/30"
                }`}
              >
                {done ? "✓" : i + 1}
              </span>

              <button
                disabled={!ready && !isGate}
                onClick={() => onSelect(s.key)}
                aria-controls="stage-panel"
                aria-current={active ? "true" : undefined}
                aria-label={`${s.label}${isGate ? ", tu turno" : done ? ", completado" : isRunning ? ", en progreso" : !ready ? ", bloqueado" : ""}`}
                className={`mb-1 w-full rounded-lg px-3 py-2 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blueprint-500 focus-visible:ring-offset-1 ${
                  active ? "bg-tint" : ready || isGate ? "hover:bg-paper" : "cursor-not-allowed"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span
                    className={`font-display text-sm font-semibold ${
                      active ? "text-blueprint-800 dark:text-blueprint-200" : ready || isGate ? "text-ink" : "text-ink/35"
                    }`}
                  >
                    {s.label}
                  </span>
                  {s.n != null && ready && (
                    <span className="badge bg-surface font-mono text-ink/50 ring-1 ring-line">{s.n}</span>
                  )}
                </div>
                {isGate && <span className="annot mt-0.5 block text-accent-700">Tu turno</span>}
                {isRunning && <span className="annot mt-0.5 block text-blueprint-600">Trazando…</span>}
              </button>
            </li>
          );
        })}
      </ol>

      {/* Horizontal (móvil) */}
      <ol className="flex gap-2 overflow-x-auto pb-1 lg:hidden">
        {stages.map((s, i) => {
          const ready = readySet.has(s.key);
          const done = doneSet.has(s.key);
          const isGate = gateKey === s.key;
          const active = activeKey === s.key;
          return (
            <li key={s.key} className="shrink-0">
              <button
                disabled={!ready && !isGate}
                onClick={() => onSelect(s.key)}
                aria-controls="stage-panel"
                aria-current={active ? "true" : undefined}
                aria-label={`${s.label}${isGate ? ", tu turno" : done ? ", completado" : !ready ? ", bloqueado" : ""}`}
                className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blueprint-500 focus-visible:ring-offset-1 ${
                  active
                    ? "border-blueprint-500 bg-tint text-blueprint-800 dark:text-blueprint-200"
                    : isGate
                    ? "border-accent-500 bg-accent-500/15 text-accent-700"
                    : ready
                    ? "border-line bg-surface text-ink/70"
                    : "border-line bg-paper text-ink/35"
                }`}
              >
                <span className="font-mono text-[11px]">{done ? "✓" : i + 1}</span>
                {s.label}
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
