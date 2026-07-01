"""Rubrica de evaluacion DSR: mide la CALIDAD del diseno experimental generado.

El alcance de la tesis es la calidad del diseno (no la ejecucion). Esta rubrica
es un instrumento estructural y deterministico (no requiere LLM) derivado de las
reglas de Testing Business Ideas. Devuelve sub-puntajes 0..1 y un puntaje global.

Dimensiones:
1. hypotheses_quality      - hipotesis comprobables, suficientes y con contra-hipotesis.
2. risk_coverage           - cobertura de Deseabilidad/Factibilidad/Viabilidad.
3. prioritization_soundness- priorizacion 'riesgo primero' coherente (importante + sin evidencia).
4. experiment_selection    - experimentos validos, multiples por hipotesis riesgosa, discovery->validation, respeta presupuesto.
5. metrics_criteria        - metricas y criterios presentes, con umbrales comparables.
6. pitfalls_avoided        - el critico aprueba / sin issues de severidad alta.
"""
from __future__ import annotations

import re

from app.catalog.service import get_experiment

WEIGHTS = {
    "hypotheses_quality": 0.18,
    "risk_coverage": 0.15,
    "prioritization_soundness": 0.17,
    "experiment_selection": 0.25,
    "metrics_criteria": 0.15,
    "pitfalls_avoided": 0.10,
}

_BUDGET_MAX_COST = {"very_low": 1, "low": 2, "medium": 3, "high": 5}


def _hypotheses_quality(bp: dict) -> float:
    hyps = bp.get("hypotheses", [])
    if not hyps:
        return 0.0
    score = 0.0
    score += 0.4 if len(hyps) >= 6 else len(hyps) / 6 * 0.4
    testable = sum(1 for h in hyps if h.get("statement", "").lower().startswith("creemos"))
    score += 0.3 * (testable / len(hyps))
    score += 0.3 if any(h.get("is_counter_hypothesis") for h in hyps) else 0.0
    return round(min(score, 1.0), 3)


def _risk_coverage(bp: dict) -> float:
    types = {c.get("risk_type") for c in bp.get("classifications", [])}
    types.discard(None)
    return round(len(types) / 3, 3)  # 1.0 si cubre D, F y V


def _prioritization_soundness(bp: dict) -> float:
    prio = bp.get("prioritization", [])
    if not prio:
        return 0.0
    riskiest = [p for p in prio if p.get("is_riskiest")]
    if not riskiest:
        return 0.2
    coherent = sum(
        1 for p in riskiest if p.get("importance", 0) >= 0.6 and p.get("evidence", 1) <= 0.4
    )
    return round(min(1.0, 0.4 + 0.6 * (coherent / len(riskiest))), 3)


def _experiment_selection(bp: dict) -> float:
    recs = bp.get("recommendations", [])
    prio = bp.get("prioritization", [])
    if not recs:
        return 0.0
    riskiest_ids = [p["hypothesis_id"] for p in prio if p.get("is_riskiest")] or [
        p["hypothesis_id"] for p in prio
    ]

    by_hyp: dict[str, list] = {}
    for r in recs:
        by_hyp.setdefault(r["hypothesis_id"], []).append(r)

    # cobertura: cada hipotesis riesgosa tiene >=1 experimento
    covered = sum(1 for hid in riskiest_ids if by_hyp.get(hid))
    coverage = covered / len(riskiest_ids) if riskiest_ids else 0.0

    # triangulacion: alguna riesgosa con >=2 experimentos
    triangulation = 1.0 if any(len(by_hyp.get(hid, [])) >= 2 for hid in riskiest_ids) else 0.0

    # ids validos (anclaje al catalogo)
    valid = sum(1 for r in recs if get_experiment(r["experiment_id"])) / len(recs)

    # respeta presupuesto
    max_cost = _BUDGET_MAX_COST.get((bp.get("constraints", {}) or {}).get("budget_level", "low"), 5)
    budget_ok = sum(1 for r in recs if r.get("cost", 5) <= max_cost) / len(recs)

    return round(0.35 * coverage + 0.25 * triangulation + 0.25 * valid + 0.15 * budget_ok, 3)


def _metrics_criteria(bp: dict) -> float:
    cards = bp.get("test_cards", [])
    if not cards:
        return 0.0
    score = 0.0
    for c in cards:
        has_metric = bool(c.get("metric", "").strip())
        has_crit = bool(c.get("success_criteria", "").strip())
        comparable = bool(re.search(r"\d", c.get("success_criteria", "")))  # umbral numerico
        score += (0.4 * has_metric + 0.3 * has_crit + 0.3 * comparable)
    return round(score / len(cards), 3)


def _pitfalls_avoided(bp: dict) -> float:
    review = bp.get("critic_review")
    if not review:
        return 0.5
    if review.get("passed"):
        return 1.0
    high = sum(1 for i in review.get("issues", []) if i.get("severity") == "high")
    return round(max(0.0, 0.6 - 0.2 * high), 3)


def score_blueprint(bp: dict) -> dict:
    """Devuelve sub-puntajes y el puntaje global ponderado (0..1)."""
    subs = {
        "hypotheses_quality": _hypotheses_quality(bp),
        "risk_coverage": _risk_coverage(bp),
        "prioritization_soundness": _prioritization_soundness(bp),
        "experiment_selection": _experiment_selection(bp),
        "metrics_criteria": _metrics_criteria(bp),
        "pitfalls_avoided": _pitfalls_avoided(bp),
    }
    overall = round(sum(subs[k] * WEIGHTS[k] for k in subs), 3)
    return {"subscores": subs, "overall": overall}
