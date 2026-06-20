from typing import Any, Optional
from pydantic import BaseModel, Field

from app.optimization.resource_optimizer import (
    OptimizationInput,
    ResourceOptimizer,
    ResourcePlan,
)


class ScenarioInput(BaseModel):
    impact_score: float = Field(..., ge=0, le=100)
    closure_probability: float = Field(..., ge=0, le=1)
    priority: str

    expected_crowd_size: int = Field(..., ge=0)
    event_duration_hours: float = Field(..., gt=0)
    peak_hour: bool
    nearby_sensitive_zone: bool

    max_manpower: int = Field(default=60, gt=0)
    max_barricades: int = Field(default=40, gt=0)
    max_patrol_units: int = Field(default=15, gt=0)
    max_emergency_units: int = Field(default=8, gt=0)


class ScenarioModification(BaseModel):
    impact_score: Optional[float] = Field(default=None, ge=0, le=100)
    closure_probability: Optional[float] = Field(default=None, ge=0, le=1)
    priority: Optional[str] = None

    expected_crowd_size: Optional[int] = Field(default=None, ge=0)
    event_duration_hours: Optional[float] = Field(default=None, gt=0)
    peak_hour: Optional[bool] = None
    nearby_sensitive_zone: Optional[bool] = None

    max_manpower: Optional[int] = Field(default=None, gt=0)
    max_barricades: Optional[int] = Field(default=None, gt=0)
    max_patrol_units: Optional[int] = Field(default=None, gt=0)
    max_emergency_units: Optional[int] = Field(default=None, gt=0)


class WhatIfInput(BaseModel):
    original_scenario: ScenarioInput
    modifications: ScenarioModification


class WhatIfResult(BaseModel):
    original_scenario: dict[str, Any]
    modified_scenario: dict[str, Any]
    original_plan: ResourcePlan
    modified_plan: ResourcePlan
    comparison: dict[str, Any]


class WhatIfSimulator:
    def __init__(self):
        self.optimizer = ResourceOptimizer()

    def run(self, data: WhatIfInput) -> WhatIfResult:
        original_dict = data.original_scenario.model_dump()

        modifications = data.modifications.model_dump(exclude_none=True)
        modified_dict = {
            **original_dict,
            **modifications,
        }

        original_plan = self.optimizer.optimize(
            OptimizationInput(**original_dict)
        )

        modified_plan = self.optimizer.optimize(
            OptimizationInput(**modified_dict)
        )

        comparison = {
            "manpower_change": modified_plan.manpower - original_plan.manpower,
            "barricades_change": modified_plan.barricades - original_plan.barricades,
            "patrol_units_change": modified_plan.patrol_units - original_plan.patrol_units,
            "emergency_units_change": modified_plan.emergency_units - original_plan.emergency_units,
            "risk_level_change": {
                "from": original_plan.risk_level,
                "to": modified_plan.risk_level,
            },
        }

        return WhatIfResult(
            original_scenario=original_dict,
            modified_scenario=modified_dict,
            original_plan=original_plan,
            modified_plan=modified_plan,
            comparison=comparison,
        )