"""Restricciones del equipo (budget / tiempo / etapa)."""
from __future__ import annotations

from pydantic import BaseModel

from app.schemas.enums import BudgetLevel, Stage, TimeHorizon


class Constraints(BaseModel):
    budget_level: BudgetLevel = BudgetLevel.low
    time_horizon: TimeHorizon = TimeHorizon.weeks
    stage: Stage = Stage.discovery
