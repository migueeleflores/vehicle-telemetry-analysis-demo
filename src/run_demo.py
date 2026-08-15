"""Run the complete synthetic telemetry analysis demo."""

from __future__ import annotations

from .generate_data import generate_dataset
from .lap_analysis import compare_laps
from .plotting import plot_delta_time, plot_driver_inputs, plot_speed_comparison
from .telemetry_loader import load_telemetry


def main() -> None:
    dataset_path = generate_dataset()
    data = load_telemetry(dataset_path)
    metrics = compare_laps(data)

    print("\nLap comparison\n")
    printable = metrics.copy()
    printable["lap_time_s"] = printable["lap_time_s"].map(lambda value: f"{value:.3f}")
    printable["average_speed_kmh"] = printable["average_speed_kmh"].map(lambda value: f"{value:.1f}")
    printable["minimum_speed_kmh"] = printable["minimum_speed_kmh"].map(lambda value: f"{value:.1f}")
    printable["maximum_speed_kmh"] = printable["maximum_speed_kmh"].map(lambda value: f"{value:.1f}")
    printable["braking_fraction"] = printable["braking_fraction"].map(lambda value: f"{100 * value:.1f}%")
    printable["full_throttle_fraction"] = printable["full_throttle_fraction"].map(lambda value: f"{100 * value:.1f}%")
    print(printable.to_string(index=False))

    baseline_time = float(metrics.loc[metrics["lap"] == "baseline", "lap_time_s"].iloc[0])
    improved_time = float(metrics.loc[metrics["lap"] == "improved", "lap_time_s"].iloc[0])
    print(f"\nTime gain: {baseline_time - improved_time:.3f} s")

    outputs = [
        plot_speed_comparison(data),
        plot_driver_inputs(data),
        plot_delta_time(data),
    ]
    print("\nGenerated outputs:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
