"""Punto de entrada para LangGraph Studio (`langgraph dev`).

Expone el grafo del enjambre SIN compilar; la plataforma de LangGraph aporta la
persistencia (checkpointer) y el manejo de interrupts/human-in-the-loop desde la UI.
No afecta a la app FastAPI (que sigue usando build_blueprint_graph con su checkpointer).
"""
from app.graph.build_graph import make_graph_builder

graph = make_graph_builder()
