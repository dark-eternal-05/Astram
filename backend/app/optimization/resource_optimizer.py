from pydantic import BaseModel, Field


class OptimizationInput(BaseModel):
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


class ResourcePlan(BaseModel):
    manpower: int
    barricades: int
    patrol_units: int
    emergency_units: int
    risk_level: str
    explanation: list[str]


class ResourceOptimizer:
    def optimize(self, data: OptimizationInput) -> ResourcePlan:
        explanation = []

        manpower = 4
        barricades = 2
        patrol_units = 1
        emergency_units = 0

        if data.expected_crowd_size >= 5000:
            manpower += 6
            barricades += 4
            explanation.append("Crowd size above 5,000 increases manpower and barricade need.")

        if data.expected_crowd_size >= 15000:
            manpower += 10
            barricades += 6
            patrol_units += 2
            explanation.append("Large crowd above 15,000 requires additional patrol coverage.")

        if data.impact_score >= 70:
            manpower += 10
            barricades += 8
            patrol_units += 2
            explanation.append("High impact score increases field deployment.")

        elif data.impact_score >= 40:
            manpower += 5
            barricades += 4
            patrol_units += 1
            explanation.append("Moderate impact score requires controlled deployment.")

        if data.closure_probability >= 0.7:
            barricades += 8
            patrol_units += 2
            explanation.append("High closure probability increases barricading and patrol units.")

        if data.peak_hour:
            manpower += 4
            patrol_units += 1
            explanation.append("Peak-hour event needs extra traffic control.")

        if data.nearby_sensitive_zone:
            manpower += 4
            emergency_units += 1
            explanation.append("Nearby sensitive zone requires emergency readiness.")

        if data.event_duration_hours >= 4:
            manpower += 4
            explanation.append("Long event duration increases manpower requirement.")

        priority = data.priority.lower()

        if priority == "high":
            manpower += 5
            barricades += 4
            emergency_units += 1
            explanation.append("High priority event receives additional safety resources.")

        elif priority == "critical":
            manpower += 10
            barricades += 6
            patrol_units += 2
            emergency_units += 2
            explanation.append("Critical priority event receives maximum safety reinforcement.")

        manpower = min(manpower, data.max_manpower)
        barricades = min(barricades, data.max_barricades)
        patrol_units = min(patrol_units, data.max_patrol_units)
        emergency_units = min(emergency_units, data.max_emergency_units)

        risk_level = self._risk_level(data.impact_score, data.closure_probability)

        if not explanation:
            explanation.append("Low-risk event requires baseline deployment only.")

        return ResourcePlan(
            manpower=manpower,
            barricades=barricades,
            patrol_units=patrol_units,
            emergency_units=emergency_units,
            risk_level=risk_level,
            explanation=explanation,
        )

    def _risk_level(self, impact_score: float, closure_probability: float) -> str:
        if impact_score >= 75 or closure_probability >= 0.75:
            return "high"
        if impact_score >= 45 or closure_probability >= 0.45:
            return "medium"
        return "low"