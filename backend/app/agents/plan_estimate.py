"""Plan Estimation Agent (determinista): suma costo/esfuerzo/capacidades y avisa si excede.

No usa LLM: lee el catálogo real para los experimentos elegidos y compara con las
restricciones del equipo. Cifras exactas y auditables.
"""
from __future__ import annotations

from app.agents.base import trace
from app.catalog import service
from app.schemas.plan import PlanEstimate
from app.schemas.state import BlueprintState

_BUDGET_MAX_COST = {"very_low": 1, "low": 2, "medium": 3, "high": 5}
_TIME_MAX_RUN = {"days": 2, "weeks": 3, "months": 5}


def plan_estimate_node(state: BlueprintState) -> dict:
    recs = state.get("recommendations", [])
    constraints = state.get("constraints", {}) or {}
    budget_max = _BUDGET_MAX_COST.get(constraints.get("budget_level", "low"), 2)
    time_max = _TIME_MAX_RUN.get(constraints.get("time_horizon", "weeks"), 3)

    total_cost = effort = max_cost = 0
    caps: set[str] = set()
    over_budget: list[str] = []
    over_time: list[str] = []

    for r in recs:
        e = service.get_experiment(r.get("experiment_id"))
        if not e:
            continue
        total_cost += e.cost
        effort += e.setup_time + e.run_time
        max_cost = max(max_cost, e.cost)
        caps.update(e.capabilities or [])
        if e.cost > budget_max:
            over_budget.append(e.name)
        if e.run_time > time_max:
            over_time.append(e.name)

    warnings: list[str] = []
    if over_budget:
        warnings.append(f"{len(over_budget)} experimento(s) superan tu presupuesto ({constraints.get('budget_level', 'low')}).")
    if over_time:
        warnings.append(f"{len(over_time)} experimento(s) podrían no caber en tu horizonte ({constraints.get('time_horizon', 'weeks')}).")

    est = PlanEstimate(
        experiment_count=len(recs),
        total_cost_points=total_cost,
        total_effort_points=effort,
        max_cost=max_cost,
        required_capabilities=sorted(caps),
        within_budget=not over_budget,
        within_time=not over_time,
        warnings=warnings,
    )
    fit = "dentro de" if not over_budget else "excede"
    return {
        "plan_estimate": est.model_dump(mode="json"),
        "messages": [trace("plan_estimate", f"Plan: {len(recs)} experimentos, costo {total_cost} pts, {fit} presupuesto.")],
    }
