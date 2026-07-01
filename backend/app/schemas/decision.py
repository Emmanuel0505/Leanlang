"""Salida del Decision Agent (Learning Card): regla de decision pre-comprometida.

Sigue en la fase de DISENO: define QUE haremos segun el resultado, ANTES de ejecutar
el experimento (pre-registro de la decision, anti-sesgo). No captura resultados reales.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas._validators import coerce_enum
from app.schemas.enums import Decision


class DecisionRule(BaseModel):
    """Regla de decision por experimento: la 'Learning Card' del libro, pre-llenada."""

    hypothesis_id: str
    experiment_id: str
    if_validated: str = Field(description="Que haremos si se cumple el criterio de exito")
    if_invalidated: str = Field(description="Que haremos si NO se cumple")
    recommended_decision: Decision = Field(
        default=Decision.persevere, description="Inclinacion por defecto: persevere | pivot | kill"
    )

    @field_validator("recommended_decision", mode="before")
    @classmethod
    def _dec(cls, v):
        return coerce_enum(v, Decision, Decision.persevere)


class DecisionRuleList(BaseModel):
    decisions: list[DecisionRule]
