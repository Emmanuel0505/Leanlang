"""Enumeraciones del dominio (alineadas con Testing Business Ideas)."""
from __future__ import annotations

from enum import Enum


class RiskType(str, Enum):
    """Los tres riesgos del libro."""

    desirability = "desirability"  # deseabilidad: quieren esto?
    feasibility = "feasibility"  # factibilidad: podemos construirlo/entregarlo?
    viability = "viability"  # viabilidad: deberiamos hacerlo? (genera dinero?)


class BMCBlock(str, Enum):
    """Bloques del Business Model Canvas + Value Proposition Canvas."""

    customer_segments = "customer_segments"
    value_propositions = "value_propositions"
    channels = "channels"
    customer_relationships = "customer_relationships"
    revenue_streams = "revenue_streams"
    key_resources = "key_resources"
    key_activities = "key_activities"
    key_partners = "key_partners"
    cost_structure = "cost_structure"
    # VPC
    customer_jobs = "customer_jobs"
    pains = "pains"
    gains = "gains"


class RiskLevel(str, Enum):
    """Nivel de riesgo de una hipotesis (priorizacion del Risk Agent)."""

    high = "high"  # alto: importante y sin evidencia -> probar primero
    medium = "medium"
    low = "low"


class Stage(str, Enum):
    discovery = "discovery"
    validation = "validation"


class Decision(str, Enum):
    """Decision pre-comprometida (Learning Card): que hacer segun el resultado."""

    persevere = "persevere"  # continuar: la evidencia respalda seguir
    pivot = "pivot"  # cambiar: ajustar la hipotesis/propuesta
    kill = "kill"  # descartar: la evidencia invalida la idea


class BudgetLevel(str, Enum):
    very_low = "very_low"
    low = "low"
    medium = "medium"
    high = "high"


class TimeHorizon(str, Enum):
    days = "days"
    weeks = "weeks"
    months = "months"


class Quadrant(str, Enum):
    """Cuadrantes del Assumptions Map (importancia x evidencia)."""

    test_now = "test_now"  # importante + sin evidencia  -> experimentar primero
    keep_evidence = "keep_evidence"  # importante + con evidencia -> documentar/cuestionar
    deprioritize = "deprioritize"  # no importante + con evidencia
    park = "park"  # no importante + sin evidencia
