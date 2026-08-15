"""Plotting utilities for telemetry comparison outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .lap_analysis import calculate_delta_time


def _prepare_output_dir(output_dir: str | Path) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def plot_speed_comparison(data: pd.DataFrame, output_dir: str | Path = "outputs") -> Path:
    output = _prepare_output_dir(output_dir) / "speed_comparison.png"
    fig, ax = plt.subplots(figsize=(11, 5))
    for lap_name, lap in data.groupby("lap", sort=False):
        ax.plot(lap["distance_m"], lap["speed_kmh"], label=lap_name.title())
    ax.set_title("Speed Comparison")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Speed [km/h]")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


def plot_driver_inputs(data: pd.DataFrame, output_dir: str | Path = "outputs") -> Path:
    output = _prepare_output_dir(output_dir) / "driver_inputs.png"
    fig, ax = plt.subplots(figsize=(11, 5))
    for lap_name, lap in data.groupby("lap", sort=False):
        ax.plot(lap["distance_m"], lap["throttle"], label=f"{lap_name.title()} throttle")
        ax.plot(lap["distance_m"], lap["brake"], linestyle="--", label=f"{lap_name.title()} brake")
    ax.set_title("Driver Inputs")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Normalized input")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output


def plot_delta_time(data: pd.DataFrame, output_dir: str | Path = "outputs") -> Path:
    baseline = data[data["lap"] == "baseline"]
    improved = data[data["lap"] == "improved"]
    delta = calculate_delta_time(baseline, improved)

    output = _prepare_output_dir(output_dir) / "delta_time.png"
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(delta["distance_m"], delta["delta_s"])
    ax.axhline(0.0, linewidth=1)
    ax.set_title("Improved Lap vs Baseline — Time Delta")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Delta [s]")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output
