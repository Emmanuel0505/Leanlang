"""Agente 7: Coach / Critico (QA) -> audita el diseno contra las trampas del libro."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import jdump, trace
from app.agents.prompts import CRITIC_PROMPT_VERSION, CRITIC_SYSTEM
from app.core.llm import get_structured_model
from app.eval.rubric import score_blueprint
from app.schemas.state import BlueprintState
from app.schemas.testcard import CriticReview


def critic_node(state: BlueprintState) -> dict:
    blueprint = {
        "hypotheses": state.get("hypotheses", []),
        "classifications": state.get("classifications", []),
        "prioritization": state.get("prioritization", []),
        "recommendations": state.get("recommendations", []),
        "metric_specs": state.get("metric_specs", []),
        "success_criteria": state.get("success_criteria", []),
        "decisions": state.get("decisions", []),
        "validation_roadmap": state.get("validation_roadmap", {}),
        "plan_estimate": state.get("plan_estimate", {}),
        "test_cards": state.get("test_cards", []),
        "constraints": state.get("constraints", {}),
    }

    # Rubrica deterministica (app/eval/rubric.py): los mismos 6 criterios
    # ponderados que se usan para la evaluacion academica (DSR) del sistema,
    # calculados sin LLM a partir de datos estructurales (cuantas hipotesis
    # tienen contra-hipotesis, si cubre D/F/V, si prioriza riesgo primero,
    # etc). Pedirle a un LLM que se autoevalue con un solo float "calidad
    # global", sin ningun criterio explicito, es la receta clasica para un
    # juez mal calibrado: el score varia entre corridas identicas, se agrupa
    # cerca del umbral de aprobacion y no discrimina bien entre un diseno
    # mediocre y uno solido. Anclar el numero que decide passed/revision a
    # esta rubrica lo hace reproducible y consistente con como se evalua el
    # proyecto en el resto del codigo (ver tests/test_rubric.py).
    rubric = score_blueprint(blueprint)

    model = get_structured_model(CriticReview, tier="high")
    msgs = [
        SystemMessage(content=CRITIC_SYSTEM),
        HumanMessage(
            content=(
                f"Desglose objetivo de calidad (rubrica DSR, 0 a 1 por dimension -- "
                f"tu propio quality_score debe ser consistente con este desglose):\n"
                f"{jdump(rubric)}\n\n"
                f"Audita este diseno experimental completo:\n\n{jdump(blueprint)}"
            )
        ),
    ]
    review: CriticReview = model.invoke(msgs)

    # El LLM sigue aportando lo que la rubrica no puede medir con reglas
    # estructurales (issues cualitativos con severidad, sesgo de confirmacion,
    # summary en prosa) -- pero el NUMERO que decide si el blueprint pasa o
    # vuelve a revision es siempre el de la rubrica, nunca el autoreporte del
    # LLM: evita que una corrida "generosa" del LLM apruebe un diseno flojo
    # (o viceversa).
    review.quality_score = rubric["overall"]
    has_high_issue = any(i.severity == "high" for i in review.issues)
    review.passed = review.quality_score >= 0.7 and not has_high_issue

    revision_count = state.get("revision_count", 0)
    status = "OK" if review.passed else f"requiere mejoras ({len(review.issues)} issues)"
    return {
        "critic_review": review.model_dump(mode="json"),
        "revision_count": revision_count,
        "messages": [trace("critic", f"Calidad {review.quality_score:.2f} -> {status}.", version=CRITIC_PROMPT_VERSION)],
    }
