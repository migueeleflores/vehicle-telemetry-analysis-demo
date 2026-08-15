"""Loading and validation helpers for telemetry CSV files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "lap",
    "distance_m",
    "time_s",
    "speed_kmh",
    "throttle",
    "brake",
    "steering_deg",
    "gear",
}


class TelemetryValidationError(ValueError):
    """Raised when telemetry data does not satisfy the demo schema."""


def validate_telemetry(data: pd.DataFrame) -> None:
    """Validate required columns and basic signal ranges."""
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise TelemetryValidationError(f"Missing required columns: {sorted(missing)}")

    if data.empty:
        raise TelemetryValidationError("Telemetry dataset is empty.")

    if data[list(REQUIRED_COLUMNS - {"lap"})].isna().any().any():
        raise TelemetryValidationError("Telemetry contains missing numeric values.")

    if not data["throttle"].between(0.0, 1.0).all():
        raise TelemetryValidationError("Throttle must remain between 0 and 1.")

    if not data["brake"].between(0.0, 1.0).all():
        raise TelemetryValidationError("Brake must remain between 0 and 1.")

    for lap_name, lap in data.groupby("lap"):
        if len(lap) < 10:
            raise TelemetryValidationError(f"Lap '{lap_name}' has too few samples.")
        if not lap["distance_m"].is_monotonic_increasing:
            raise TelemetryValidationError(f"Distance is not monotonic for lap '{lap_name}'.")
        if not lap["time_s"].is_monotonic_increasing:
            raise TelemetryValidationError(f"Time is not monotonic for lap '{lap_name}'.")


def load_telemetry(path: str | Path) -> pd.DataFrame:
    """Read a telemetry CSV file and validate its schema."""
    data = pd.read_csv(Path(path))
    validate_telemetry(data)
    return data
