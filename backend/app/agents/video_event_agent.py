from pathlib import Path
from typing import Any

import cv2
from pydantic import BaseModel, Field


class VideoEventInference(BaseModel):
    event_cause: str
    confidence: float = Field(..., ge=0, le=1)
    traffic_density: int = Field(..., ge=0, le=100)
    average_speed_kmph: int = Field(..., ge=0)
    expected_crowd_size: int = Field(..., ge=0)
    involves_heavy_vehicle: bool
    is_planned: bool
    is_authenticated: bool
    reasoning: list[str]
    source_trace: dict[str, Any]


class VideoEventAgent:
    """
    Demo-safe video signal agent.

    It does not pretend to perform production-grade object detection.
    It extracts simple video statistics and converts them into traceable
    traffic/event signals for the ASTRaM pipeline.
    """

    def analyze(self, video_path: str) -> VideoEventInference:
        path = Path(video_path)

        if not path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        cap = cv2.VideoCapture(str(path))

        if not cap.isOpened():
            raise ValueError("Could not open uploaded video.")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 25)
        duration_seconds = frame_count / fps if fps > 0 else 0

        sampled_frames = 0
        motion_scores = []
        brightness_scores = []

        previous_gray = None

        max_samples = 60
        sample_every = max(1, frame_count // max_samples) if frame_count else 1

        current_frame = 0

        while True:
            ok, frame = cap.read()

            if not ok:
                break

            if current_frame % sample_every != 0:
                current_frame += 1
                continue

            resized = cv2.resize(frame, (320, 180))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

            brightness_scores.append(float(gray.mean()))

            if previous_gray is not None:
                diff = cv2.absdiff(previous_gray, gray)
                motion_scores.append(float(diff.mean()))

            previous_gray = gray
            sampled_frames += 1
            current_frame += 1

        cap.release()

        avg_motion = sum(motion_scores) / len(motion_scores) if motion_scores else 0
        avg_brightness = (
            sum(brightness_scores) / len(brightness_scores)
            if brightness_scores
            else 0
        )

        traffic_density = self._estimate_density(avg_motion)
        average_speed = self._estimate_speed(traffic_density)
        expected_crowd = self._estimate_crowd(traffic_density, duration_seconds)

        event_cause = self._classify_event(traffic_density, avg_motion)
        confidence = self._confidence(sampled_frames, duration_seconds)

        reasoning = [
            f"Sampled {sampled_frames} frames from uploaded video.",
            f"Average motion score: {round(avg_motion, 2)}.",
            f"Estimated traffic density: {traffic_density}%.",
            f"Estimated average speed: {average_speed} km/h.",
        ]

        if traffic_density >= 75:
            reasoning.append("High density suggests congestion or crowd buildup.")
        elif traffic_density >= 45:
            reasoning.append("Moderate density suggests controlled traffic load.")
        else:
            reasoning.append("Low density suggests normal movement.")

        return VideoEventInference(
            event_cause=event_cause,
            confidence=confidence,
            traffic_density=traffic_density,
            average_speed_kmph=average_speed,
            expected_crowd_size=expected_crowd,
            involves_heavy_vehicle=traffic_density >= 70,
            is_planned=False,
            is_authenticated=True,
            reasoning=reasoning,
            source_trace={
                "video_file": path.name,
                "frame_count": frame_count,
                "fps": fps,
                "duration_seconds": round(duration_seconds, 2),
                "sampled_frames": sampled_frames,
                "avg_motion_score": round(avg_motion, 2),
                "avg_brightness": round(avg_brightness, 2),
            },
        )

    def _estimate_density(self, avg_motion: float) -> int:
        density = int(min(max(avg_motion * 5, 10), 95))
        return density

    def _estimate_speed(self, density: int) -> int:
        if density >= 80:
            return 10
        if density >= 60:
            return 18
        if density >= 40:
            return 28
        return 42

    def _estimate_crowd(self, density: int, duration_seconds: float) -> int:
        base = density * 220

        if duration_seconds > 120:
            base += 2000

        return int(min(max(base, 1000), 50000))

    def _classify_event(self, density: int, avg_motion: float) -> str:
        if density >= 80:
            return "congestion"
        if density >= 60:
            return "public_event"
        if avg_motion >= 8:
            return "incident"
        return "normal_traffic"

    def _confidence(self, sampled_frames: int, duration_seconds: float) -> float:
        if sampled_frames >= 40 and duration_seconds >= 10:
            return 0.82
        if sampled_frames >= 20:
            return 0.68
        return 0.5