"""Hipotesis de negocio y su clasificacion/priorizacion."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas._validators import clamp, coerce_enum
from app.schemas.enums import BMCBlock, Quadrant, RiskLevel, RiskType


class Hypothesis(BaseModel):
    """Hipotesis bien formada: testable, precisa, discreta ('Creemos que...')."""

    id: str = Field(description="Identificador corto y estable, ej. 'h1'")
    statement: str = Field(description="Enunciado 'Creemos que...' (testable, preciso, discreto)")
    source_block: BMCBlock = Field(description="Bloque BMC/VPC del que surge")
    is_counter_hypothesis: bool = Field(
        default=False, description="True si es una contra-hipotesis (anti-sesgo de confirmacion)"
    )

    @field_validator("source_block", mode="before")
    @classmethod
    def _block(cls, v):
        return coerce_enum(v, BMCBlock, BMCBlock.value_propositions)


class HypothesisList(BaseModel):
    hypotheses: list[Hypothesis]


class Classification(BaseModel):
    """Salida del Risk Agent, por hipotesis: tipo, bloque y nivel de riesgo."""

    hypothesis_id: str
    risk_type: RiskType
    risk_level: RiskLevel = Field(default=RiskLevel.medium, description="Nivel de riesgo: high|medium|low")
    bmc_block: BMCBlock
    rationale: str = Field(description="Por que se clasifica asi (1-2 frases)")

    @field_validator("risk_type", mode="before")
    @classmethod
    def _risk(cls, v):
        return coerce_enum(v, RiskType, RiskType.desirability)

    @field_validator("risk_level", mode="before")
    @classmethod
    def _level(cls, v):
        return coerce_enum(v, RiskLevel, RiskLevel.medium)

    @field_validator("bmc_block", mode="before")
    @classmethod
    def _block(cls, v):
        return coerce_enum(v, BMCBlock, BMCBlock.value_propositions)


class ClassificationList(BaseModel):
    classifications: list[Classification]


class Prioritization(BaseModel):
    """Salida del Priorizador (Assumptions Map 2x2)."""

    hypothesis_id: str
    importance: float = Field(ge=0.0, le=1.0, description="0=irrelevante, 1=critica para la idea")
    evidence: float = Field(ge=0.0, le=1.0, description="0=sin evidencia, 1=evidencia fuerte")
    quadrant: Quadrant
    is_riskiest: bool = Field(description="True si es importante + sin evidencia (probar primero)")
    rationale: str

    @field_validator("importance", "evidence", mode="before")
    @classmethod
    def _unit(cls, v):
        return clamp(v, 0.0, 1.0)

    @field_validator("quadrant", mode="before")
    @classmethod
    def _quad(cls, v):
        return coerce_enum(v, Quadrant, Quadrant.test_now)


class PrioritizationList(BaseModel):
    prioritization: list[Prioritization]
