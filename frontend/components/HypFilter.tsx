"use client";

/** Filtro por hipótesis: chips compartidos entre Experimentos y Test Cards. */
export function HypFilter({ ids, value, onChange }: { ids: string[]; value: string | null; onChange: (v: string | null) => void }) {
  if (ids.length <= 1) return null;
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="annot mr-1">Filtrar:</span>
      <button
        onClick={() => onChange(null)}
        aria-pressed={value === null}
        className={`rounded-full border px-2.5 py-0.5 text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blueprint-500 ${
          value === null ? "border-blueprint-500 bg-tint text-blueprint-700 dark:text-blueprint-200" : "border-line bg-surface text-ink/60 hover:text-ink"
        }`}
      >
        Todas
      </button>
      {ids.map((id) => (
        <button
          key={id}
          onClick={() => onChange(id === value ? null : id)}
          aria-pressed={value === id}
          aria-label={`Filtrar por ${id}`}
          className={`rounded-full border px-2.5 py-0.5 font-mono text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blueprint-500 ${
            value === id ? "border-blueprint-500 bg-tint text-blueprint-700 dark:text-blueprint-200" : "border-line bg-surface text-ink/60 hover:text-ink"
          }`}
        >
          {id}
        </button>
      ))}
    </div>
  );
}
