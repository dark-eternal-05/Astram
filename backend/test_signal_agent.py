from app.schemas.signal_schema import RawSignalInput
from app.agents.signal_structuring_agent import SignalStructuringAgent


raw_signal = RawSignalInput(
    manual_report="Heavy crowd expected near stadium gate 2.",
    event_feed={
        "event_name": "City Football Final",
        "event_type": "sports",
        "location": "Central Stadium Road",
        "expected_crowd_size": 18000,
        "event_duration_hours": 5,
        "peak_hour": True,
        "road_type": "arterial",
        "nearby_sensitive_zone": True,
    },
    weather_input={
        "weather_condition": "rain"
    },
    cctv_metadata={
        "location": "Backup CCTV Location",
        "estimated_crowd_size": 12000,
    },
)

agent = SignalStructuringAgent()
structured = agent.structure(raw_signal)

print(structured.model_dump())