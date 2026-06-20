from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


SourceType = Literal[
    "manual_report",
    "cctv_metadata",
    "drone_metadata",
    "weather_input",
    "event_feed",
    "fallback",
]


class TrackedField(BaseModel):
    value: Any
    source: SourceType
    confidence: float = Field(..., ge=0.0, le=1.0)
    fallback_used: bool = False

    @field_validator("value")
    @classmethod
    def value_must_not_be_empty(cls, value: Any):
        if value is None:
            raise ValueError("value cannot be None")

        if isinstance(value, str) and not value.strip():
            raise ValueError("value cannot be empty")

        return value


class RawSignalInput(BaseModel):
    manual_report: Optional[str] = None
    cctv_metadata: Optional[dict] = None
    drone_metadata: Optional[dict] = None
    weather_input: Optional[dict] = None
    event_feed: Optional[dict] = None

    @field_validator(
        "manual_report",
        "cctv_metadata",
        "drone_metadata",
        "weather_input",
        "event_feed",
        mode="after",
    )
    @classmethod
    def at_least_one_signal_required(cls, value):
        return value


class StructuredSignal(BaseModel):
    event_name: TrackedField
    event_type: TrackedField
    location: TrackedField
    expected_crowd_size: TrackedField
    event_duration_hours: TrackedField
    weather_condition: TrackedField
    peak_hour: TrackedField
    road_type: TrackedField
    nearby_sensitive_zone: TrackedField
    manual_report_text: Optional[TrackedField] = None


class CSVReadySignalRow(BaseModel):
    event_name: str
    event_type: str
    location: str

    expected_crowd_size: int = Field(..., ge=0)
    event_duration_hours: float = Field(..., gt=0)

    weather_condition: Literal[
        "clear",
        "cloudy",
        "rain",
        "heavy_rain",
        "fog",
        "storm",
        "unknown",
    ]

    peak_hour: bool

    road_type: Literal[
        "arterial",
        "collector",
        "local",
        "highway",
        "unknown",
    ]

    nearby_sensitive_zone: bool
    manual_report_text: Optional[str] = None

    @field_validator("event_name", "event_type", "location")
    @classmethod
    def required_strings_must_not_be_empty(cls, value: str):
        if not value.strip():
            raise ValueError("field cannot be empty")
        return value.strip()