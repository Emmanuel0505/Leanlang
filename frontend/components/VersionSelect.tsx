"use client";

export interface BlueprintVersion {
  id: string;
  status: string;
  created_at?: string;
}

const STATUS_LABEL: Record<string, string> = {
  done: "completado",
  awaiting_input: "en pausa",
  running: "en curso",
};

/** Selector de versiones del blueprint (historial por proyecto). */
export function VersionSelect({
  versions,
  currentId,
  onSelect,
}: {
  versions: BlueprintVersion[];
  currentId: string | null;
  onSelect: (id: string) => void;
}) {
  if (versions.length <= 1) return null;
  const total = versions.length;
  return (
    <label className="inline-flex items-center gap-2">
      <span className="annot">Versión</span>
      <select
        value={currentId ?? ""}
        onChange={(e) => onSelect(e.target.value)}
        className="rounded-xl border border-line bg-surface px-3 py-2 text-sm text-ink shadow-sm focus:border-blueprint-400 focus:outline-none focus:ring-4 focus:ring-blueprint-500/10"
      >
        {versions.map((v, i) => (
          <option key={v.id} value={v.id}>
            v{total - i}{i === 0 ? " · más reciente" : ""} · {STATUS_LABEL[v.status] ?? v.status}
          </option>
        ))}
      </select>
    </label>
  );
}
