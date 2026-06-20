from app.schemas.signal_schema import CSVReadySignalRow, StructuredSignal


class CSVValidationError(Exception):
    pass


class CSVValidator:
    """
    Converts structured tracked fields into one clean model-ready CSV row.

    This validator:
    - Preserves strict schema validation through Pydantic.
    - Rejects invalid model input.
    - Produces a plain dictionary ready for CSV writing or model inference.
    """

    def validate_structured_signal(self, structured_signal: StructuredSignal) -> CSVReadySignalRow:
        try:
            csv_row = CSVReadySignalRow(
                event_name=str(structured_signal.event_name.value),
                event_type=str(structured_signal.event_type.value),
                location=str(structured_signal.location.value),
                expected_crowd_size=int(structured_signal.expected_crowd_size.value),
                event_duration_hours=float(structured_signal.event_duration_hours.value),
                weather_condition=str(structured_signal.weather_condition.value),
                peak_hour=bool(structured_signal.peak_hour.value),
                road_type=str(structured_signal.road_type.value),
                nearby_sensitive_zone=bool(structured_signal.nearby_sensitive_zone.value),
                manual_report_text=(
                    str(structured_signal.manual_report_text.value)
                    if structured_signal.manual_report_text
                    else None
                ),
            )

            return csv_row

        except Exception as exc:
            raise CSVValidationError(f"CSV validation failed: {exc}") from exc

    def to_csv_dict(self, structured_signal: StructuredSignal) -> dict:
        validated_row = self.validate_structured_signal(structured_signal)
        return validated_row.model_dump()