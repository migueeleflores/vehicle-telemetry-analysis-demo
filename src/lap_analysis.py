"""Engineering metrics for synthetic racing laps."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LapMetrics:
    lap: str
    lap_time_s: float
    average_speed_kmh: float
    minimum_speed_kmh: float
    maximum_speed_kmh: float
    braking_fraction: float
    full_throttle_fraction: float


def calculate_lap_time(lap: pd.DataFrame) -> float:
    """Estimate total lap time using the final timestamp plus the final sample interval."""
    if len(lap) < 2:
        raise ValueError("At least two telemetry samples are required.")
    final_interval = float(lap["time_s"].iloc[-1] - lap["time_s"].iloc[-2])
    return float(lap["time_s"].iloc[-1] + final_interval)


def calculate_metrics(lap: pd.DataFrame) -> LapMetrics:
    """Calculate a compact set of driver- and vehicle-facing lap metrics."""
    lap_name = str(lap["lap"].iloc[0])
    return LapMetrics(
        lap=lap_name,
        lap_time_s=calculate_lap_time(lap),
        average_speed_kmh=float(lap["speed_kmh"].mean()),
        minimum_speed_kmh=float(lap["speed_kmh"].min()),
        maximum_speed_kmh=float(lap["speed_kmh"].max()),
        braking_fraction=float((lap["brake"] > 0.05).mean()),
        full_throttle_fraction=float((lap["throttle"] > 0.95).mean()),
    )


def compare_laps(data: pd.DataFrame) -> pd.DataFrame:
    """Return one row of engineering metrics per lap."""
    rows = [calculate_metrics(lap) for _, lap in data.groupby("lap", sort=False)]
    return pd.DataFrame([row.__dict__ for row in rows])


def interpolate_elapsed_time(lap: pd.DataFrame, distance_grid: np.ndarray) -> np.ndarray:
    """Interpolate elapsed time onto a common distance grid."""
    return np.interp(distance_grid, lap["distance_m"], lap["time_s"])


def calculate_delta_time(
    baseline: pd.DataFrame,
    comparison: pd.DataFrame,
    points: int = 500,
) -> pd.DataFrame:
    """Calculate comparison-minus-baseline elapsed-time delta over lap distance."""
    max_distance = min(float(baseline["distance_m"].max()), float(comparison["distance_m"].max()))
    distance_grid = np.linspace(0.0, max_distance, points)
    baseline_time = interpolate_elapsed_time(baseline, distance_grid)
    comparison_time = interpolate_elapsed_time(comparison, distance_grid)

    return pd.DataFrame(
        {
            "distance_m": distance_grid,
            "delta_s": comparison_time - baseline_time,
        }
    )
