from app.schemas.signal_schema import RawSignalInput, StructuredSignal, TrackedField


class SignalStructuringAgent:
    """
    Simple rule-based signal structuring agent.

    Rules:
    - Does not hallucinate unsupported values.
    - Every extracted field includes value, source, confidence, fallback_used.
    - Fallbacks are explicit and low-confidence.
    """

    def structure(self, raw_signal: RawSignalInput) -> StructuredSignal:
        event_feed = raw_signal.event_feed or {}
        weather_input = raw_signal.weather_input or {}
        cctv_metadata = raw_signal.cctv_metadata or {}
        drone_metadata = raw_signal.drone_metadata or {}

        manual_report = raw_signal.manual_report

        return StructuredSignal(
            event_name=self._extract_event_name(event_feed),
            event_type=self._extract_event_type(event_feed),
            location=self._extract_location(event_feed, cctv_metadata, drone_metadata),
            expected_crowd_size=self._extract_crowd_size(event_feed, cctv_metadata, drone_metadata),
            event_duration_hours=self._extract_duration(event_feed),
            weather_condition=self._extract_weather(weather_input),
            peak_hour=self._extract_peak_hour(event_feed),
            road_type=self._extract_road_type(event_feed),
            nearby_sensitive_zone=self._extract_sensitive_zone(event_feed),
            manual_report_text=self._extract_manual_report(manual_report),
        )

    def _tracked(self, value, source, confidence, fallback_used=False) -> TrackedField:
        return TrackedField(
            value=value,
            source=source,
            confidence=confidence,
            fallback_used=fallback_used,
        )

    def _fallback(self, value):
        return self._tracked(
            value=value,
            source="fallback",
            confidence=0.2,
            fallback_used=True,
        )

    def _extract_event_name(self, event_feed: dict) -> TrackedField:
        if event_feed.get("event_name"):
            return self._tracked(event_feed["event_name"], "event_feed", 0.95)
        return self._fallback("unknown_event")

    def _extract_event_type(self, event_feed: dict) -> TrackedField:
        if event_feed.get("event_type"):
            return self._tracked(event_feed["event_type"], "event_feed", 0.9)
        return self._fallback("unknown")

    def _extract_location(self, event_feed: dict, cctv_metadata: dict, drone_metadata: dict) -> TrackedField:
        if event_feed.get("location"):
            return self._tracked(event_feed["location"], "event_feed", 0.95)

        if cctv_metadata.get("location"):
            return self._tracked(cctv_metadata["location"], "cctv_metadata", 0.75)

        if drone_metadata.get("location"):
            return self._tracked(drone_metadata["location"], "drone_metadata", 0.75)

        return self._fallback("unknown_location")

    def _extract_crowd_size(self, event_feed: dict, cctv_metadata: dict, drone_metadata: dict) -> TrackedField:
        if event_feed.get("expected_crowd_size") is not None:
            return self._tracked(int(event_feed["expected_crowd_size"]), "event_feed", 0.9)

        if cctv_metadata.get("estimated_crowd_size") is not None:
            return self._tracked(int(cctv_metadata["estimated_crowd_size"]), "cctv_metadata", 0.7)

        if drone_metadata.get("estimated_crowd_size") is not None:
            return self._tracked(int(drone_metadata["estimated_crowd_size"]), "drone_metadata", 0.7)

        return self._fallback(0)

    def _extract_duration(self, event_feed: dict) -> TrackedField:
        if event_feed.get("event_duration_hours") is not None:
            return self._tracked(float(event_feed["event_duration_hours"]), "event_feed", 0.9)
        return self._fallback(1.0)

    def _extract_weather(self, weather_input: dict) -> TrackedField:
        if weather_input.get("weather_condition"):
            return self._tracked(weather_input["weather_condition"], "weather_input", 0.9)
        return self._fallback("unknown")

    def _extract_peak_hour(self, event_feed: dict) -> TrackedField:
        if event_feed.get("peak_hour") is not None:
            return self._tracked(bool(event_feed["peak_hour"]), "event_feed", 0.85)
        return self._fallback(False)

    def _extract_road_type(self, event_feed: dict) -> TrackedField:
        if event_feed.get("road_type"):
            return self._tracked(event_feed["road_type"], "event_feed", 0.85)
        return self._fallback("unknown")

    def _extract_sensitive_zone(self, event_feed: dict) -> TrackedField:
        if event_feed.get("nearby_sensitive_zone") is not None:
            return self._tracked(bool(event_feed["nearby_sensitive_zone"]), "event_feed", 0.85)
        return self._fallback(False)

    def _extract_manual_report(self, manual_report: str | None) -> TrackedField | None:
        if manual_report:
            return self._tracked(manual_report, "manual_report", 0.8)
        return None