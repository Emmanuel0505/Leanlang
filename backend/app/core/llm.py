"""Fabrica de modelos LLM agnostica.

Usa `init_chat_model` de LangChain para que el motor de los agentes pueda
intercambiarse por configuracion (anthropic / openai / etc.) sin tocar el
codigo de los agentes. Esto facilita la comparacion de modelos en la tesis.
"""
from __future__ import annotations

from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings


@lru_cache
def get_model(temperature: float | None = None) -> BaseChatModel:
    """Devuelve el chat model configurado por env (cacheado).

    Soporta endpoints compatibles con OpenAI (DeepSeek, Groq, Together, Ollama...)
    via LLM_BASE_URL y LLM_API_KEY.
    """
    kwargs: dict = {}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    if settings.llm_api_key:
        kwargs["api_key"] = settings.llm_api_key
    return init_chat_model(
        model=settings.llm_model,
        model_provider=settings.llm_provider,
        temperature=settings.llm_temperature if temperature is None else temperature,
        **kwargs,
    )


def get_structured_model(schema, temperature: float | None = None):
    """Modelo con salida estructurada validada contra un schema Pydantic.

    Usa function-calling (tools), compatible con OpenAI/Anthropic/DeepSeek, en lugar
    de json_schema (que no todos los endpoints compatibles soportan).

    `with_retry` reintenta cuando el modelo devuelve una salida vacia o mal formada
    (p. ej. DeepSeek a veces responde `{}`), evitando que una corrida entera falle
    por una respuesta puntualmente invalida.
    """
    structured = get_model(temperature=temperature).with_structured_output(
        schema, method="function_calling"
    )
    return structured.with_retry(stop_after_attempt=3)
