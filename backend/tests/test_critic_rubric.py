"""Tests del Critic: el quality_score/passed que decide la ruta del grafo viene
siempre de la rubrica deterministica (app/eval/rubric.py), nunca del autoreporte
del LLM -- ver app/agents/critic.py para el razonamiento completo. Sin esto, un
LLM "generoso" podria aprobar un diseno objetivamente flojo."""
from __future__ import annotations

from app.agents.critic import critic_node
from app.eval.rubric import score_blueprint

_WEAK_BLUEPRINT_STATE = {
    # Una sola hipotesis, sin contra-hipotesis, sin clasificar riesgo, sin
    # recomendaciones ni test cards: deberia puntuar bajo en casi todas las
    # dimensiones de la rubrica (hypotheses_quality, risk_coverage,
    # experiment_selection, metrics_criteria).
    "hypotheses": [{"id": "h1", "statement": "Creemos que los usuarios pagaran.", "is_counter_hypothesis": False}],
    "classifications": [],
    "prioritization": [],
    "recommendations": [],
    "metric_specs": [],
    "success_criteria": [],
    "decisions": [],
    "validation_roadmap": {},
    "plan_estimate": {},
    "test_cards": [],
    "constraints": {"budget_level": "low"},
    "revision_count": 0,
}


def test_quality_score_comes_from_rubric_not_from_llm_self_report(fake_llm):
    """El LLM falso (via fake_llm) siempre devuelve quality_score=0.82,
    passed=True, issues=[] (ver tests/conftest.py::_canned). Con un blueprint
    objetivamente debil, el critico real debe ignorar ese autoreporte
    optimista y usar la rubrica -- que para este blueprint da un score bajo."""
    expected_rubric = score_blueprint(_WEAK_BLUEPRINT_STATE)
    assert expected_rubric["overall"] < 0.7, "el blueprint de prueba deberia puntuar bajo por diseno"

    result = critic_node(_WEAK_BLUEPRINT_STATE)
    review = result["critic_review"]

    assert review["quality_score"] == expected_rubric["overall"]
    assert review["quality_score"] != 0.82  # no es el valor canned del LLM falso
    assert review["passed"] is False  # por debajo del umbral 0.7, pese a que el LLM decia passed=True


def test_high_severity_issue_blocks_passed_even_with_good_rubric_score(fake_llm, monkeypatch):
    """Aunque la rubrica de un score alto, un issue de severidad 'high' que
    reporte el LLM (ej. sesgo de confirmacion que la rubrica no detecta por
    reglas estructurales) debe seguir bloqueando `passed`."""
    import app.agents.critic as critic_module
    from app.schemas.testcard import CriticIssue, CriticReview

    strong_state = {
        "hypotheses": [
            {"id": "h1", "statement": "Creemos que X.", "is_counter_hypothesis": False},
            {"id": "h2", "statement": "Creemos que Y.", "is_counter_hypothesis": True},
        ] * 3,
        "classifications": [
            {"hypothesis_id": "h1", "risk_type": t} for t in ("desirability", "feasibility", "viability")
        ],
        "prioritization": [{"hypothesis_id": "h1", "is_riskiest": True, "importance": 0.9, "evidence": 0.1}],
        "recommendations": [
            {"hypothesis_id": "h1", "experiment_id": "customer-interview", "cost": 1},
            {"hypothesis_id": "h1", "experiment_id": "link-tracking", "cost": 1},
        ],
        "metric_specs": [],
        "success_criteria": [],
        "decisions": [],
        "validation_roadmap": {},
        "plan_estimate": {},
        "test_cards": [
            {"metric": "CTR", "success_criteria": ">= 5%"},
            {"metric": "N entrevistas", "success_criteria": ">= 7 de 10"},
        ],
        "constraints": {"budget_level": "low"},
        "revision_count": 0,
    }
    rubric = score_blueprint(strong_state)
    assert rubric["overall"] >= 0.7, "este blueprint de prueba deberia puntuar alto por diseno"

    def fake_with_high_issue(schema, temperature=None, tier=None):
        class _Fake:
            def invoke(self, _msgs):
                return CriticReview(
                    quality_score=0.95,
                    passed=True,
                    issues=[CriticIssue(pitfall="sesgo de confirmacion", severity="high", detail="x", suggestion="y")],
                    summary="x",
                )
        return _Fake()

    monkeypatch.setattr(critic_module, "get_structured_model", fake_with_high_issue)

    result = critic_node(strong_state)
    review = result["critic_review"]
    assert review["quality_score"] == rubric["overall"]
    assert review["passed"] is False  # el issue 'high' bloquea pese al score alto
