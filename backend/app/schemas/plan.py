"""Salida del Plan Estimation Agent: costo/tiempo/capacidades del plan completo.

Determinista (no LLM): se calcula desde el catálogo real, por lo que las cifras son
exactas y auditables (no alucinadas) — clave para una estimación de costos.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class PlanEstimate(BaseModel):
    experiment_count: int = 0
    total_cost_points: int = Field(0, description="Suma de costos (escala 1-5 del catálogo)")
    total_effort_points: int = Field(0, description="Suma de setup_time + run_time")
    max_cost: int = Field(0, description="Costo del experimento más caro del plan")
    required_capabilities: list[str] = Field(default_factory=list, description="Capacidades que el equipo necesitará")
    within_budget: bool = True
    within_time: bool = True
    warnings: list[str] = Field(default_factory=list)
