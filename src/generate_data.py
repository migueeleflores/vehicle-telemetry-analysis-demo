"""Generate deterministic synthetic racing telemetry for two comparable laps."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

TRACK_LENGTH_M = 4200.0
SAMPLES_PER_LAP = 900
REQUIRED_COLUMNS = [
    "lap",
    "distance_m",
    "time_s",
    "speed_kmh",
    "throttle",
    "brake",
    "steering_deg",
    "gear",
]


def _corner_slowdown(position: np.ndarray, center: float, width: float, depth: float) -> np.ndarray:
    """Return a smooth speed reduction centered on a normalized lap position."""
    wrapped = np.minimum(np.abs(position - center), 1.0 - np.abs(position - center))
    return depth * np.exp(-0.5 * (wrapped / width) ** 2)


def _build_speed_profile(position: np.ndarray, lap: str) -> np.ndarray:
    base_speed = 258.0 + 18.0 * np.sin(2.0 * np.pi * position - 0.4)

    corners = [
        (0.10, 0.024, 122.0),
        (0.24, 0.035, 78.0),
        (0.39, 0.028, 108.0),
        (0.57, 0.040, 88.0),
        (0.72, 0.025, 115.0),
        (0.88, 0.036, 92.0),
    ]
    speed = base_speed.copy()
    for center, width, depth in corners:
        speed -= _corner_slowdown(position, center, width, depth)

    if lap == "improved":
        # The improved lap carries slightly more speed through three key corners.
        speed += 5.5 * np.exp(-0.5 * ((position - 0.24) / 0.045) ** 2)
        speed += 4.0 * np.exp(-0.5 * ((position - 0.57) / 0.055) ** 2)
        speed += 4.5 * np.exp(-0.5 * ((position - 0.88) / 0.045) ** 2)
        speed += 1.2

    return np.clip(speed, 72.0, 305.0)


def _derive_inputs(speed: np.ndarray, lap: str) -> tuple[np.ndarray, np.ndarray]:
    gradient = np.gradient(speed)

    brake = np.clip((-gradient - 0.05) / 1.7, 0.0, 1.0)
    throttle = np.clip(1.0 + gradient / 2.0, 0.0, 1.0)

    low_speed = speed < 165.0
    throttle[low_speed] *= 0.72

    if lap == "improved":
        # Slightly cleaner exits and shorter braking phases.
        brake = np.clip(brake * 0.92, 0.0, 1.0)
        throttle = np.clip(throttle + 0.025, 0.0, 1.0)

    throttle[brake > 0.05] = 0.0

    return throttle, brake


def _build_lap(lap: str) -> pd.DataFrame:
    position = np.linspace(0.0, 1.0, SAMPLES_PER_LAP, endpoint=False)
    distance_m = position * TRACK_LENGTH_M
    speed_kmh = _build_speed_profile(position, lap)
    throttle, brake = _derive_inputs(speed_kmh, lap)

    # Integrate elapsed time from distance and speed.
    speed_ms = speed_kmh / 3.6
    segment_distance = TRACK_LENGTH_M / SAMPLES_PER_LAP
    dt = segment_distance / speed_ms
    time_s = np.concatenate(([0.0], np.cumsum(dt[:-1])))

    steering_deg = (
        11.0 * np.sin(12.0 * np.pi * position)
        + 5.0 * np.sin(26.0 * np.pi * position + 0.5)
    )
    gear = np.clip(np.floor((speed_kmh - 55.0) / 34.0) + 1, 1, 8).astype(int)

    return pd.DataFrame(
        {
            "lap": lap,
            "distance_m": np.round(distance_m, 3),
            "time_s": np.round(time_s, 4),
            "speed_kmh": np.round(speed_kmh, 3),
            "throttle": np.round(throttle, 4),
            "brake": np.round(brake, 4),
            "steering_deg": np.round(steering_deg, 3),
            "gear": gear,
        }
    )


def generate_dataset(output_path: str | Path = "data/synthetic_laps.csv") -> Path:
    """Generate the demo dataset and return the written CSV path."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    data = pd.concat([_build_lap("baseline"), _build_lap("improved")], ignore_index=True)
    data.to_csv(output, index=False)
    return output


if __name__ == "__main__":
    path = generate_dataset()
    print(f"Synthetic telemetry written to {path}")
