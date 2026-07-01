"""Catalogo de experimentos y recomendaciones del Selector."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas._validators import clamp, coerce_enum
from app.schemas.enums import RiskType, Stage


class ExperimentCatalogItem(BaseModel):
    """Un experimento de la biblioteca de 44 (estructura del catalogo)."""

    id: str
    name: str
    category: Stage
    subcategory: str
    types: list[RiskType]
    cost: int = Field(ge=1, le=5)
    setup_time: int = Field(ge=1, le=5)
    run_time: int = Field(ge=1, le=5)
    evidence_strength: int = Field(ge=1, le=5)
    capabilities: list[str] = Field(default_factory=list)
    description: str
    pairings_before: list[str] = Field(default_factory=list)
    pairings_after: list[str] = Field(default_factory=list)
    page_ref: int | None = None


class ExperimentRec(BaseModel):
    """Recomendacion de experimento para una hipotesis (salida del Selector)."""

    hypothesis_id: str
    experiment_id: str
    experiment_name: str
    sequence_order: int = Field(description="Orden sugerido (1 = primero, mas barato/rapido)")
    stage: Stage
    rationale: str = Field(description="Por que este experimento, dadas restricciones y reglas")
    design_detail: str = Field(
        default="",
        description="Diseno concreto del experimento: guion de entrevista, copy de landing, alcance del MVP, pasos del test...",
    )
    expected_evidence_strength: int = Field(ge=1, le=5)
    cost: int = Field(ge=1, le=5)

    @field_validator("stage", mode="before")
    @classmethod
    def _stage(cls, v):
        return coerce_enum(v, Stage, Stage.discovery)

    @field_validator("expected_evidence_strength", "cost", mode="before")
    @classmethod
    def _scale(cls, v):
        return int(clamp(v, 1, 5))


class ExperimentRecList(BaseModel):
    recommendations: list[ExperimentRec]
