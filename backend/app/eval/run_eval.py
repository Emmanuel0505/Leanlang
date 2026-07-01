"""Runner de evaluacion DSR.

Ejecuta el grafo de agentes sobre el golden set (auto-aceptando los interrupts),
puntua cada blueprint con la rubrica estructural y escribe results.json.

Requiere un LLM configurado (ANTHROPIC_API_KEY / OPENAI_API_KEY). Uso:
    python -m app.eval.run_eval
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from app.api.streaming import serialize_blueprint
from app.eval.rubric import score_blueprint
from app.graph.build_graph import build_blueprint_graph

_GOLDEN = Path(__file__).parent / "golden_set.json"
_OUT = Path(__file__).parent / "results.json"


def run_case(graph, case: dict) -> dict:
    cfg = {"configurable": {"thread_id": f"eval-{case['id']}"}}
    initial = {
        "project_id": case["id"],
        "user_id": "eval",
        "raw_idea": case["raw_idea"],
        "constraints": case["constraints"],
        "revision_count": 0,
        "messages": [],
    }
    t0 = time.time()
    graph.invoke(initial, config=cfg)
    # Auto-aceptar todos los interrupts hasta finalizar (max 5 por seguridad)
    for _ in range(5):
        snap = graph.get_state(cfg)
        if not snap.next:
            break
        graph.invoke(Command(resume={"accepted": True}), config=cfg)
    elapsed = round(time.time() - t0, 2)

    values = graph.get_state(cfg).values or {}
    bp = serialize_blueprint(values)
    bp["constraints"] = case["constraints"]
    result = score_blueprint(bp)
    return {"case": case["id"], "seconds": elapsed, **result}


def main() -> None:
    cases = json.loads(_GOLDEN.read_text(encoding="utf-8"))
    graph = build_blueprint_graph(MemorySaver())
    results = [run_case(graph, c) for c in cases]
    overall = round(sum(r["overall"] for r in results) / len(results), 3)
    payload = {"mean_overall": overall, "results": results}
    _OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
