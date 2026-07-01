"""Salidas del Metrics Agent y del Success Criteria Agent (separadas en el enjambre)."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas._validators import clamp


class MetricSpec(BaseModel):
    """Metrica accionable para un experimento (Metrics Agent)."""

    hypothesis_id: str
    experiment_id: str
    metric: str = Field(description="Que se mide, observable y concreto ('Y mediremos...')")
    data_source: str = Field(default="", description="De donde se obtiene el dato")
    rationale: str = Field(default="", description="Por que esta metrica es accionable")


class MetricSpecList(BaseModel):
    metrics: list[MetricSpec]


class SuccessCriterion(BaseModel):
    """Criterio de exito + umbral de validacion (Success Criteria Agent)."""

    hypothesis_id: str
    experiment_id: str
    criterion: str = Field(description="'Acertamos si...' criterio de exito claro")
    threshold: str = Field(description="Umbral cuantitativo y comparable (ej. '>= 30% de conversion')")
    expected_evidence_strength: int = Field(ge=1, le=5, description="Fuerza de evidencia esperada 1-5")

    @field_validator("expected_evidence_strength", mode="before")
    @classmethod
    def _scale(cls, v):
        return int(clamp(v, 1, 5))


class SuccessCriterionList(BaseModel):
    success_criteria: list[SuccessCriterion]
