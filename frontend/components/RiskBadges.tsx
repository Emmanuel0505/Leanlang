import type { RiskType } from "@/lib/types";

const LABEL: Record<RiskType, string> = {
  desirability: "Deseabilidad",
  feasibility: "Factibilidad",
  viability: "Viabilidad",
};
const COLOR: Record<RiskType, string> = {
  desirability: "bg-desire-soft text-desire-ink",
  feasibility: "bg-feas-soft text-feas-ink",
  viability: "bg-viab-soft text-viab-ink",
};
const DOT: Record<RiskType, string> = {
  desirability: "bg-desire",
  feasibility: "bg-feas",
  viability: "bg-viab",
};

export function RiskBadge({ type }: { type?: RiskType }) {
  if (!type) return null;
  return (
    <span className={`badge ${COLOR[type]}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${DOT[type]}`} />
      {LABEL[type]}
    </span>
  );
}
