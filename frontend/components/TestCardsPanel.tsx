"use client";

import { useMemo } from "react";
import type { DecisionRule, TestCard } from "@/lib/types";
import { TestCardView } from "./TestCardView";
import { HypFilter } from "./HypFilter";

export function TestCardsPanel({
  cards,
  decisions,
  focusHyp,
  onFocus,
}: {
  cards: TestCard[];
  decisions?: DecisionRule[];
  focusHyp: string | null;
  onFocus: (v: string | null) => void;
}) {
  const ids = useMemo(() => Array.from(new Set(cards.map((c) => c.hypothesis_id))).sort(), [cards]);
  const decByKey = useMemo(
    () => Object.fromEntries((decisions || []).map((d) => [`${d.hypothesis_id}:${d.experiment_id}`, d])),
    [decisions],
  );
  const filtered = focusHyp ? cards.filter((c) => c.hypothesis_id === focusHyp) : cards;

  return (
    <div className="space-y-4">
      <HypFilter ids={ids} value={focusHyp} onChange={onFocus} />
      <div className="grid gap-3 md:grid-cols-2">
        {filtered.map((c, i) => (
          <TestCardView key={i} card={c} decision={decByKey[`${c.hypothesis_id}:${c.experiment_id}`]} />
        ))}
      </div>
    </div>
  );
}
