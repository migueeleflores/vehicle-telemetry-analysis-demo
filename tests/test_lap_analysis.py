from __future__ import annotations

import pandas as pd
import pytest

from src.generate_data import generate_dataset
from src.lap_analysis import (
    calculate_average_speed,
    calculate_delta_time,
    calculate_lap_distance,
    compare_laps,
)
from src.telemetry_loader import TelemetryValidationError, load_telemetry, validate_telemetry


def test_generated_dataset_contains_two_valid_laps(tmp_path):
    path = generate_dataset(tmp_path / "synthetic_laps.csv")
    data = load_telemetry(path)

    assert set(data["lap"].unique()) == {"baseline", "improved"}
    assert len(data) > 1000


def test_improved_lap_is_faster(tmp_path):
    data = load_telemetry(generate_dataset(tmp_path / "synthetic_laps.csv"))
    metrics = compare_laps(data).set_index("lap")

    assert metrics.loc["improved", "lap_time_s"] < metrics.loc["baseline", "lap_time_s"]


def test_average_speed_uses_distance_over_time(tmp_path):
    data = load_telemetry(generate_dataset(tmp_path / "synthetic_laps.csv"))
    baseline = data[data["lap"] == "baseline"]
    improved = data[data["lap"] == "improved"]

    assert calculate_lap_distance(baseline) == pytest.approx(4200.0, abs=0.01)
    assert calculate_average_speed(baseline) == pytest.approx(205.069, abs=0.01)
    assert calculate_average_speed(improved) == pytest.approx(208.107, abs=0.01)


def test_delta_finishes_negative_for_improved_lap(tmp_path):
    data = load_telemetry(generate_dataset(tmp_path / "synthetic_laps.csv"))
    baseline = data[data["lap"] == "baseline"]
    improved = data[data["lap"] == "improved"]
    delta = calculate_delta_time(baseline, improved)

    assert delta["delta_s"].iloc[-1] < 0.0


def test_validation_rejects_missing_columns():
    invalid = pd.DataFrame({"lap": ["baseline"], "speed_kmh": [100.0]})

    with pytest.raises(TelemetryValidationError):
        validate_telemetry(invalid)
