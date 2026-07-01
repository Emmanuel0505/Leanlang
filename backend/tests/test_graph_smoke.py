"""Smoke test del grafo completo con LLM falso: valida orquestacion + interrupts + loop."""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.graph.build_graph import build_blueprint_graph


def _initial_state():
    return {
        "project_id": "p1",
        "user_id": "u1",
        "raw_idea": "Kits de ciencia por suscripcion mensual para padres millennials.",
        "constraints": {"budget_level": "low", "time_horizon": "weeks", "stage": "discovery"},
        "revision_count": 0,
        "messages": [],
    }


def test_full_flow_with_three_interrupts(fake_llm):
    graph = build_blueprint_graph(MemorySaver())
    config = {"configurable": {"thread_id": "t-smoke"}}

    # 1) Corre hasta el primer interrupt (revisar hipotesis)
    graph.invoke(_initial_state(), config=config)
    snap = graph.get_state(config)
    assert snap.next, "deberia pausar en human_hypotheses"
    assert "human_hypotheses" in snap.next
    assert len(snap.values["hypotheses"]) == 3

    # 2) Reanuda aceptando hipotesis -> pausa en priorizacion
    graph.invoke(Command(resume={"accepted": True}), config=config)
    snap = graph.get_state(config)
    assert "human_prioritization" in snap.next
    riskiest = [p for p in snap.values["prioritization"] if p["is_riskiest"]]
    assert len(riskiest) == 2

    # 3) Reanuda aceptando priorizacion -> selector/metrics/critic -> pausa en aprobacion
    graph.invoke(Command(resume={"accepted": True}), config=config)
    snap = graph.get_state(config)
    assert "human_approval" in snap.next

    # El selector debe haber descartado el id inventado ('inventado-xyz')
    recs = snap.values["recommendations"]
    assert recs, "deberia haber recomendaciones"
    assert all(r["experiment_id"] in {"link-tracking", "customer-interview"} for r in recs)
    assert all(r["experiment_id"] != "inventado-xyz" for r in recs)

    # Test cards y revision del critico presentes
    assert snap.values["test_cards"]
    assert snap.values["critic_review"]["passed"] is True

    # 4) Reanuda aprobando -> termina
    graph.invoke(Command(resume={"approved": True}), config=config)
    snap = graph.get_state(config)
    assert not snap.next, "el grafo deberia haber terminado"


def test_human_edits_override_hypotheses(fake_llm):
    graph = build_blueprint_graph(MemorySaver())
    config = {"configurable": {"thread_id": "t-edit"}}
    graph.invoke(_initial_state(), config=config)

    edited = [{"id": "h1", "statement": "Hipotesis editada por el usuario", "source_block": "value_propositions", "is_counter_hypothesis": False}]
    graph.invoke(Command(resume={"hypotheses": edited}), config=config)
    snap = graph.get_state(config)
    assert snap.values["hypotheses"][0]["statement"] == "Hipotesis editada por el usuario"
