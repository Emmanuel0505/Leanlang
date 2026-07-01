/**
 * "Cota" de plano técnico: etiqueta + barra con marcas + valor en mono.
 * Sirve para escalas 0–1 (fracción) o 1–max (puntos).
 */
export function Dimension({
  label,
  value,
  max = 1,
  tone = "blueprint",
  fraction,
}: {
  label: string;
  value: number;
  max?: number;
  tone?: "blueprint" | "feas" | "accent" | "ink";
  fraction?: boolean;
}) {
  const pct = Math.max(0, Math.min(1, value / max)) * 100;
  const fill =
    tone === "feas" ? "bg-feas" : tone === "accent" ? "bg-accent-500" : tone === "ink" ? "bg-ink" : "bg-blueprint-500";
  const display = fraction ? value.toFixed(2) : `${Math.round(value)}/${max}`;
  return (
    <div className="flex items-center gap-2">
      <span className="annot shrink-0">{label}</span>
      <span className="relative h-1.5 w-20 overflow-hidden rounded-full bg-line/70">
        <span className={`block h-full rounded-full ${fill}`} style={{ width: `${pct}%` }} />
      </span>
      <span className="font-mono text-[11px] tabular-nums text-ink/70">{display}</span>
    </div>
  );
}
