/** Formatea un timestamp ISO (UTC) como AAAA-MM-DD en la zona horaria local del navegador. */
export function formatDateOnly(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(0, 10);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** Formatea un timestamp ISO (UTC) como HH:mm en la zona horaria local del navegador. */
export function formatTimeOnly(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(11, 16);
  return d.toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit", hour12: false });
}

const CONFIDENCE_ES: Record<string, string> = {
  high: "Alta",
  medium: "Media",
  low: "Baja",
};

/** Traduce "High/Medium/Low" (ver backend/app/schemas/research.py) al espanol; deja
 * valores numericos u otros formatos tal cual (el campo tambien admite un numero). */
export function translateConfidence(confidence: string): string {
  return CONFIDENCE_ES[confidence.trim().toLowerCase()] ?? confidence;
}
