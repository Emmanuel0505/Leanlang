"""Utilidades compartidas por los nodos/agentes."""
from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage


def trace(agent: str, text: str, *, version: str | None = None) -> AIMessage:
    """Mensaje de traza para streaming/observabilidad (incluye el nombre del agente)."""
    content = f"[{version}] {text}" if version else text
    return AIMessage(content=content, name=agent)


def jdump(obj: Any) -> str:
    """Serializa a JSON legible para meter contexto en los prompts."""
    return json.dumps(obj, ensure_ascii=False, indent=2)
