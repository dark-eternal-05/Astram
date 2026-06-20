from app.schemas.signal_schema import CSVReadySignalRow


sample = CSVReadySignalRow(
    event_name="Concert Night",
    event_type="concert",
    location="Main Road Junction",
    expected_crowd_size=5000,
    event_duration_hours=4,
    weather_condition="clear",
    peak_hour=True,
    road_type="arterial",
    nearby_sensitive_zone=False,
    manual_report_text="Heavy crowd expected near gate 2",
)

print(sample.model_dump())