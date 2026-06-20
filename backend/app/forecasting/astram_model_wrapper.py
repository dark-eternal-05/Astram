from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field


class ASTRaMForecastInput(BaseModel):
    event_cause: str
    corridor: Optional[str] = None
    zone: Optional[str] = None
    junction: Optional[str] = None

    hour: int = Field(..., ge=0, le=23)
    day_of_week: int = Field(..., ge=0, le=6)
    month: int = Field(..., ge=1, le=12)

    is_planned: Optional[bool] = None
    involves_heavy_vehicle: bool = False
    is_authenticated: bool = True


class ForecastOutput(BaseModel):
    closure_probability: float
    closure_predicted: bool
    priority: str
    priority_source: str

    expected_duration_hours_p50: float
    expected_duration_hours_p90: float

    impact_score: float
    operational_severity_score: float
    corridor_criticality: float
    cause_severity_prior: float

    resource_tier: int
    recommended_officers: int

    model_source: str
    bundle_version: str


class ASTRaMModelWrapper:
    def __init__(self, model_path: str = "models/astram_v4_model_bundle.joblib"):
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ASTRaM v4 bundle not found at {self.model_path}. "
                "Export astram_v4_model_bundle.joblib from the v4 notebook first."
            )

        self.bundle = joblib.load(self.model_path)

    def predict(self, data: ASTRaMForecastInput) -> ForecastOutput:
        event_cause = data.event_cause.lower().strip()
        corridor_filled = data.corridor if data.corridor else "Non-corridor"
        zone_filled = data.zone if data.zone else "Unzoned"

        is_weekend = int(data.day_of_week in [5, 6])
        time_segment = self._time_segment(data.hour)

        if data.is_planned is None:
            is_planned = event_cause in {
                "public_event",
                "procession",
                "vip_movement",
                "protest",
            }
        else:
            is_planned = data.is_planned

        row = {
            "event_cause": event_cause,
            "corridor_filled": corridor_filled,
            "zone_filled": zone_filled,
            "time_segment": time_segment,
            "hour": data.hour,
            "day_of_week": data.day_of_week,
            "month": data.month,
            "is_weekend": is_weekend,
            "is_planned": int(is_planned),
            "involves_heavy_vehicle": int(data.involves_heavy_vehicle),
            "is_authenticated": int(data.is_authenticated),
        }

        input_df = pd.DataFrame([row])

        cat_features = self.bundle["cat_features"]
        num_features = self.bundle["num_features"]
        model_features = cat_features + num_features

        closure_pipeline = self.bundle["closure_pipeline"]
        closure_probability = float(
            closure_pipeline.predict_proba(input_df[model_features])[0, 1]
        )

        threshold = float(self.bundle.get("closure_decision_threshold", 0.463))
        closure_predicted = closure_probability >= threshold

        priority, priority_source = self._predict_priority(
            input_df=input_df,
            corridor_filled=corridor_filled,
        )

        p50 = float(
            self.bundle["duration_p50_pipeline"]
            .predict(input_df[model_features])[0]
        )

        p90 = float(
            self.bundle["duration_p90_pipeline"]
            .predict(input_df[model_features])[0]
        )

        p50 = self._cap_duration(p50)
        p90 = self._cap_duration(p90)

        corridor_criticality = self._corridor_criticality(corridor_filled)
        cause_prior = self._cause_severity_prior(event_cause)

        severity_score = self._operational_severity_score(
            closure_probability=closure_probability,
            duration_p90=p90,
            corridor_criticality=corridor_criticality,
            event_cause=event_cause,
            is_planned=bool(is_planned),
        )

        resource_tier = self._resource_tier(severity_score)
        recommended_officers = self._recommended_officers(resource_tier)

        return ForecastOutput(
            closure_probability=round(closure_probability, 3),
            closure_predicted=bool(closure_predicted),
            priority=priority,
            priority_source=priority_source,

            expected_duration_hours_p50=round(p50, 1),
            expected_duration_hours_p90=round(p90, 1),

            impact_score=round(severity_score, 1),
            operational_severity_score=round(severity_score, 1),
            corridor_criticality=round(corridor_criticality, 3),
            cause_severity_prior=round(cause_prior, 3),

            resource_tier=resource_tier,
            recommended_officers=recommended_officers,

            model_source="astram_v4_bundle",
            bundle_version=str(self.bundle.get("bundle_version", "v4")),
        )

    def _predict_priority(self, input_df: pd.DataFrame, corridor_filled: str):
        corridor_lookup = self.bundle["corridor_lookup"]

        if corridor_filled in corridor_lookup and corridor_filled != "Non-corridor":
            return str(corridor_lookup[corridor_filled]), "corridor_lookup"

        priority_pipeline = self.bundle["priority_pipeline"]

        priority_features = (
            self.bundle["priority_cat_features"]
            + self.bundle["priority_num_features"]
        )

        high_probability = float(
            priority_pipeline.predict_proba(input_df[priority_features])[0, 1]
        )

        priority = "High" if high_probability >= 0.5 else "Low"

        return priority, "fallback_severity_model"

    def _time_segment(self, hour: int) -> str:
        if 5 <= hour < 9:
            return "morning_peak"
        if 9 <= hour < 12:
            return "late_morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 21:
            return "evening_peak"
        return "night"

    def _cap_duration(self, duration: float) -> float:
        """
        v4 keeps the notebook's p90 behavior.
        200h is not treated as an error because the notebook shows that
        long construction events genuinely hit this cap historically.
        """
        return float(min(max(duration, 0.5), 200.0))

    def _corridor_criticality(self, corridor_filled: str) -> float:
        lookup = self.bundle.get("corridor_criticality", {})
        return float(lookup.get(corridor_filled, 0.0))

    def _cause_severity_prior(self, event_cause: str) -> float:
        lookup = self.bundle.get("cause_severity_prior", {})
        return float(lookup.get(event_cause, 0.25))

    def _operational_severity_score(
        self,
        closure_probability: float,
        duration_p90: float,
        corridor_criticality: float,
        event_cause: str,
        is_planned: bool,
    ) -> float:
        cause_prior = self._cause_severity_prior(event_cause)

        duration_scaled = min(
            np.log1p(duration_p90) / np.log1p(200),
            1.0,
        )

        score = (
            0.30 * closure_probability
            + 0.25 * duration_scaled
            + 0.20 * corridor_criticality
            + 0.15 * cause_prior
            + 0.10 * float(is_planned)
        )

        return float(np.clip(score * 100, 0, 100))

    def _resource_tier(self, severity_score: float) -> int:
        if severity_score >= 75:
            return 4
        if severity_score >= 55:
            return 3
        if severity_score >= 35:
            return 2
        return 1

    def _recommended_officers(self, resource_tier: int) -> int:
        tier_to_officers = {
            1: 4,
            2: 7,
            3: 14,
            4: 24,
        }

        return tier_to_officers.get(resource_tier, 7)