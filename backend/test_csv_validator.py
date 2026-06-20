from app.agents.signal_structuring_agent import SignalStructuringAgent
from app.schemas.signal_schema import RawSignalInput
from app.validators.csv_validator import CSVValidator


raw_signal = RawSignalInput(
    manual_report="Traffic expected near stadium gate 2.",
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
)

agent = SignalStructuringAgent()
structured_signal = agent.structure(raw_signal)

validator = CSVValidator()
csv_row = validator.to_csv_dict(structured_signal)

print(csv_row)