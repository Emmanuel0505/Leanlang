"""Runtime del grafo: gestiona el checkpointer y guarda el grafo compilado.

Prioridad de checkpointer:
  1. SQLite (persistente, sin servidor) — ideal para correr sin Docker.
  2. Postgres (si se configura y esta disponible).
  3. Memoria (ultimo recurso; se pierde al reiniciar).

El grafo compilado se guarda como singleton de modulo y se inicializa en el
lifespan de FastAPI (o de forma perezosa para tests).
"""
from __future__ import annotations

from contextlib import ExitStack

from app.core.config import settings
from app.graph.build_graph import build_blueprint_graph

_graph = None


def get_graph():
    """Devuelve el grafo compilado; lo inicializa en memoria si aun no existe."""
    global _graph
    if _graph is None:
        init_graph_memory()
    return _graph


def init_graph_memory():
    """Compila el grafo con un checkpointer en memoria (dev/tests)."""
    global _graph
    from langgraph.checkpoint.memory import MemorySaver

    _graph = build_blueprint_graph(MemorySaver())
    return _graph


def init_graph_sqlite(stack: ExitStack):
    """Compila el grafo con SqliteSaver (persistente, sin servidor).

    Sobrevive a reinicios del backend: los blueprints pausados se pueden reanudar.
    `stack` (ExitStack del lifespan) mantiene viva la conexion mientras corre la app.
    """
    global _graph
    from langgraph.checkpoint.sqlite import SqliteSaver

    saver = stack.enter_context(SqliteSaver.from_conn_string(settings.checkpoint_db_path))
    saver.setup()  # crea las tablas del checkpointer si no existen
    _graph = build_blueprint_graph(saver)
    return _graph


def init_graph_postgres(stack: ExitStack):
    """Compila el grafo con PostgresSaver; cae a memoria si Postgres no esta disponible."""
    global _graph
    try:
        from langgraph.checkpoint.postgres import PostgresSaver

        saver = stack.enter_context(PostgresSaver.from_conn_string(settings.langgraph_pg_dsn))
        saver.setup()
        _graph = build_blueprint_graph(saver)
        return _graph
    except Exception as exc:  # pragma: no cover
        print(f"[runtime] Postgres checkpointer no disponible ({exc}); usando memoria.")
        return init_graph_memory()


def init_graph_persistent(stack: ExitStack):
    """Elige el mejor checkpointer disponible: SQLite -> memoria."""
    try:
        init_graph_sqlite(stack)
        print(f"[runtime] Checkpointer SQLite activo ({settings.checkpoint_db_path}).")
    except Exception as exc:  # pragma: no cover
        print(f"[runtime] SQLite checkpointer no disponible ({exc}); usando memoria.")
        init_graph_memory()
    return _graph
