"""Salida del Sequencing Agent: roadmap de validacion (orden de los experimentos)."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas._validators import coerce_enum
from app.schemas.enums import Stage


class RoadmapPhase(BaseModel):
    """Una onda/fase del plan de validacion."""

    name: str = Field(description="Nombre de la fase, ej. 'Onda 1 — Descubrimiento'")
    stage: Stage = Field(description="discovery | validation")
    goal: str = Field(description="Que busca esta fase (la pregunta que responde)")
    experiment_ids: list[str] = Field(default_factory=list, description="Experimentos del catalogo en esta fase")
    duration_estimate: str = Field(default="", description="Duracion estimada de la fase")

    @field_validator("stage", mode="before")
    @classmethod
    def _stage(cls, v):
        return coerce_enum(v, Stage, Stage.discovery)


class ValidationRoadmap(BaseModel):
    """Plan secuenciado: barato/rapido primero, evidencia creciente, triangulacion."""

    phases: list[RoadmapPhase] = Field(default_factory=list)
    rationale: str = Field(default="", description="Por que este orden (pairings, triangulacion, costo)")
