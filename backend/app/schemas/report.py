"""Salida del Report Agent: informe consolidado del blueprint de validacion."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Report(BaseModel):
    """Informe consolidado generado por el Report Agent."""

    executive_summary: str = Field(description="Resumen ejecutivo del plan de validacion (2-4 frases)")
    problem_summary: str = Field(default="", description="El problema y a quien afecta, en una frase")
    value_proposition_summary: str = Field(default="", description="La propuesta de valor, en una frase")
    riskiest_hypotheses: list[str] = Field(default_factory=list, description="Las hipotesis a probar primero")
    recommended_sequence: list[str] = Field(default_factory=list, description="Experimentos en orden sugerido")
    success_definition: str = Field(default="", description="Como sabremos que la idea esta validada")
    next_steps: list[str] = Field(default_factory=list, description="Proximos pasos accionables")


class ReportList(BaseModel):  # pragma: no cover - compat con get_structured_model si hiciera falta
    report: Report
