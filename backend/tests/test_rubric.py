"""Test de la rubrica DSR usando un blueprint generado por el grafo (LLM falso)."""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.api.streaming import serialize_blueprint
from app.eval.rubric import WEIGHTS, score_blueprint
from app.graph.build_graph import build_blueprint_graph


def _run_to_end(fake_llm):
    graph = build_blueprint_graph(MemorySaver())
    cfg = {"configurable": {"thread_id": "rubric"}}
    graph.invoke(
        {
            "project_id": "p1",
            "user_id": "u1",
            "raw_idea": "Kits de ciencia por suscripcion.",
            "constraints": {"budget_level": "low", "time_horizon": "weeks", "stage": "discovery"},
            "revision_count": 0,
            "messages": [],
        },
        config=cfg,
    )
    for _ in range(5):
        snap = graph.get_state(cfg)
        if not snap.next:
            break
        graph.invoke(Command(resume={"accepted": True}), config=cfg)
    values = graph.get_state(cfg).values or {}
    bp = serialize_blueprint(values)
    bp["constraints"] = {"budget_level": "low"}
    return bp


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_rubric_scores_generated_blueprint(fake_llm):
    bp = _run_to_end(fake_llm)
    result = score_blueprint(bp)
    assert set(result["subscores"]) == set(WEIGHTS)
    assert 0.0 <= result["overall"] <= 1.0
    # con el blueprint canned (3 hipotesis, contra-hipotesis, riesgosas, recs validas) debe ser razonable
    assert result["overall"] > 0.4
    # ids invalidos descartados -> seleccion 100% valida
    assert result["subscores"]["experiment_selection"] > 0.5


def test_rubric_empty_blueprint():
    result = score_blueprint({})
    assert result["overall"] == 0.0 or result["overall"] < 0.3
