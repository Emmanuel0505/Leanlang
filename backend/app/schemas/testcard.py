"""Test Card y revision del Critico."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas._validators import clamp


class TestCard(BaseModel):
    """Estructura de la Test Card del libro (4 pasos)."""

    hypothesis_id: str
    experiment_id: str
    # Paso 1: Hipotesis (texto), Paso 2: Test, Paso 3: Metrica, Paso 4: Criterio
    hypothesis_statement: str = Field(description="'Creemos que...'")
    test_description: str = Field(description="'Para verificarlo, vamos a...'")
    metric: str = Field(description="'Y mediremos...' (que datos se miden)")
    success_criteria: str = Field(description="'Acertamos si...' (umbral de exito)")
    expected_evidence_strength: int = Field(ge=1, le=5)
    cost: int = Field(ge=1, le=5)
    duration_estimate: str = Field(description="Estimacion de tiempo de ejecucion")

    @field_validator("expected_evidence_strength", "cost", mode="before")
    @classmethod
    def _scale(cls, v):
        return int(clamp(v, 1, 5))


class TestCardList(BaseModel):
    test_cards: list[TestCard]


class CriticIssue(BaseModel):
    pitfall: str = Field(description="Nombre de la trampa (ej. 'evidencia debil', 'pocos experimentos')")
    severity: str = Field(description="low|medium|high")
    detail: str
    suggestion: str


class CriticReview(BaseModel):
    """Salida del Coach/Critico (QA)."""

    quality_score: float = Field(ge=0.0, le=1.0, description="Calidad global del diseno experimental")
    passed: bool = Field(description="True si el blueprint supera el umbral de calidad")
    issues: list[CriticIssue] = Field(default_factory=list)
    summary: str
