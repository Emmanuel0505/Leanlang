import type { DecisionRule, DecisionType, TestCard } from "@/lib/types";
import { StatusBadge, evidenceStatus, type Status } from "./Status";

const DECISION_LABEL: Record<DecisionType, string> = { persevere: "Perseverar", pivot: "Pivotar", kill: "Descartar" };
const DECISION_STATUS: Record<DecisionType, Status> = { persevere: "ok", pivot: "warn", kill: "danger" };

export function TestCardView({ card, decision }: { card: TestCard; decision?: DecisionRule }) {
  const Row = ({ label, value }: { label: string; value: string }) => (
    <div className="border-t border-line py-2 first:border-t-0">
      <div className="annot text-blueprint-700/70">{label}</div>
      <div className="mt-0.5 text-sm leading-snug text-ink/85">{value}</div>
    </div>
  );
  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
      <div className="flex items-center justify-between border-b border-line bg-tint px-4 py-2.5">
        <h4 className="font-display text-sm font-semibold text-blueprint-800 dark:text-blueprint-200">{card.experiment_id}</h4>
        <span className="badge bg-surface font-mono text-blueprint-700 dark:text-blueprint-300">{card.hypothesis_id}</span>
      </div>
      <div className="px-4 pb-3">
        <Row label="Creemos que" value={card.hypothesis_statement} />
        <Row label="Para verificarlo" value={card.test_description} />
        <Row label="Y mediremos" value={card.metric} />
        <Row label="Acertamos si" value={card.success_criteria} />
        <div className="mt-2.5 flex flex-wrap items-center gap-2">
          <StatusBadge status={evidenceStatus(card.expected_evidence_strength)}>
            Evidencia {card.expected_evidence_strength}/5
          </StatusBadge>
          <span className="badge bg-paper text-ink/65">Costo {card.cost}/5</span>
          <span className="badge bg-paper text-ink/65">⏱ {card.duration_estimate}</span>
        </div>

        {decision && (
          <div className="mt-3 rounded-xl border border-line bg-paper/50 p-3">
            <div className="mb-1.5 flex items-center gap-2">
              <span className="annot">Decisión</span>
              <StatusBadge status={DECISION_STATUS[decision.recommended_decision]}>
                {DECISION_LABEL[decision.recommended_decision]}
              </StatusBadge>
            </div>
            <p className="text-xs leading-snug text-ink/70"><span className="font-semibold text-ok-ink">✓ Si se valida:</span> {decision.if_validated}</p>
            <p className="mt-1 text-xs leading-snug text-ink/70"><span className="font-semibold text-danger-ink">✗ Si no:</span> {decision.if_invalidated}</p>
          </div>
        )}
      </div>
    </div>
  );
}
