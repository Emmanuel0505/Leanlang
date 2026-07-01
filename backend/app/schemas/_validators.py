"""Helpers de validacion tolerante para salidas de LLM.

Modelos menos controlados (p. ej. DeepSeek) a veces devuelven valores de enum fuera
del conjunto permitido o numeros fuera de rango. En lugar de fallar toda la corrida,
coercionamos al valor valido mas cercano. Esto endurece el pipeline sin perder semantica.
"""
from __future__ import annotations

from enum import Enum
from typing import TypeVar

E = TypeVar("E", bound=Enum)


def coerce_enum(value, enum_cls: type[E], default: E) -> E:
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls(value)
    except Exception:
        if isinstance(value, str):
            low = value.strip().lower().replace(" ", "_")
            for member in enum_cls:
                if member.value == low:
                    return member
        return default


def clamp(value, lo: float, hi: float):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return lo
    return max(lo, min(hi, v))
