#!/usr/bin/env python3
"""Calculate performance thresholds from baseline measurements.

This script analyzes baseline measurements collected over 7+ days and calculates
appropriate performance thresholds using P95 + 20% safety margin.

Usage:
    python scripts/calculate_thresholds.py
    python scripts/calculate_thresholds.py --input-dir baseline-results/
    python scripts/calculate_thresholds.py --safety-margin 0.30
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import statistics
import sys
import traceback
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent


def load_baseline_files(input_dir: Path) -> list[dict[str, Any]]:
    """Load all baseline JSON files from directory.

    Args:
        input_dir: Directory containing baseline JSON files

    Returns:
        List of baseline data dictionaries
    """
    baseline_files = list(input_dir.glob("performance_baselines*.json"))

    if not baseline_files:
        raise FileNotFoundError(f"No baseline files found in {input_dir}")

    baselines = []
    for file_path in sorted(baseline_files):
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                data = json.load(f)
                baselines.append(data)
        except Exception as e:
            print(f"⚠️  Warning: Could not load {file_path}: {e}")

    if not baselines:
        raise ValueError("No valid baseline files could be loaded")

    return baselines


def aggregate_operation_stats(baselines: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Aggregate statistics across all baseline measurements.

    Args:
        baselines: List of baseline data dictionaries

    Returns:
        Dictionary mapping operation names to aggregated statistics
    """
    operation_data: dict[str, list[float]] = {}

    for baseline in baselines:
        operations = baseline.get("operations", {})
        for op_name, op_stats in operations.items():
            if op_stats.get("iterations_successful", 0) > 0:
                p95 = op_stats.get("p95", op_stats.get("max", 0))
                if p95 > 0:
                    if op_name not in operation_data:
                        operation_data[op_name] = []
                    operation_data[op_name].append(p95)

    # Calculate aggregate statistics
    aggregated = {}
    for op_name, p95_values in operation_data.items():
        if not p95_values:
            continue

        aggregated[op_name] = {
            "measurements_count": len(p95_values),
            "min_p95": min(p95_values),
            "max_p95": max(p95_values),
            "mean_p95": statistics.mean(p95_values),
            "median_p95": statistics.median(p95_values),
            "stdev_p95": statistics.stdev(p95_values) if len(p95_values) > 1 else 0,
            "aggregate_p95": sorted(p95_values)[int(len(p95_values) * 0.95)]
            if len(p95_values) >= 20
            else max(p95_values),
        }

    return aggregated


def calculate_thresholds(
    aggregated_stats: dict[str, dict[str, Any]],
    safety_margin: float = 0.20,
) -> dict[str, Any]:
    """Calculate performance thresholds with safety margin.

    Args:
        aggregated_stats: Aggregated statistics per operation
        safety_margin: Safety margin percentage (default: 0.20 = 20%)

    Returns:
        Dictionary with threshold recommendations
    """
    thresholds = {
        "metadata": {
            "generated_at": datetime.now(UTC).isoformat(),
            "safety_margin": safety_margin,
            "calculation_method": "P95 + safety_margin",
        },
        "operation_thresholds": {},
    }

    for op_name, stats in aggregated_stats.items():
        base_threshold = stats["aggregate_p95"]
        threshold_with_margin = base_threshold * (1 + safety_margin)

        thresholds["operation_thresholds"][op_name] = {
            "base_p95": round(base_threshold, 2),
            "safety_margin": safety_margin,
            "recommended_threshold": round(threshold_with_margin, 2),
            "measurements_count": stats["measurements_count"],
        }

    # Calculate overall parallel execution threshold
    if thresholds["operation_thresholds"]:
        max_threshold = max(
            t["recommended_threshold"] for t in thresholds["operation_thresholds"].values()
        )
        # Parallel execution is dominated by longest operation plus coordination overhead
        parallel_threshold = max_threshold + 10  # 10s coordination overhead

        thresholds["parallel_execution"] = {
            "recommended_threshold": round(parallel_threshold, 2),
            "per_operation_timeout": round(
                parallel_threshold * 0.5, 2
            ),  # Individual operations get 50% of total
        }

    return thresholds


def save_thresholds(thresholds: dict[str, Any], output_file: Path) -> None:
    """Save threshold recommendations to JSON file.

    Args:
        thresholds: Threshold recommendations
        output_file: Path to output JSON file
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Thresholds saved to: {output_file}")


def print_thresholds(thresholds: dict[str, Any]) -> None:
    """Print threshold recommendations in a readable format.

    Args:
        thresholds: Threshold recommendations
    """
    print("\n" + "=" * 70)
    print("PERFORMANCE THRESHOLD RECOMMENDATIONS")
    print("=" * 70)

    metadata = thresholds["metadata"]
    print(f"\nGenerated: {metadata['generated_at']}")
    print(f"Method: {metadata['calculation_method']}")
    print(f"Safety Margin: {metadata['safety_margin'] * 100}%")

    print("\n" + "-" * 70)
    print("OPERATION THRESHOLDS")
    print("-" * 70)

    for op_name, op_threshold in thresholds["operation_thresholds"].items():
        print(f"\n{op_name}:")
        print(f"  Base P95:              {op_threshold['base_p95']:.2f}s")
        print(f"  Recommended Threshold: {op_threshold['recommended_threshold']:.2f}s")
        print(f"  Based on:              {op_threshold['measurements_count']} measurements")

    if "parallel_execution" in thresholds:
        parallel = thresholds["parallel_execution"]
        print("\n" + "-" * 70)
        print("PARALLEL EXECUTION")
        print("-" * 70)
        print(f"\nRecommended Total Timeout:        {parallel['recommended_threshold']:.2f}s")
        print(f"Per-Operation Timeout:            {parallel['per_operation_timeout']:.2f}s")

    print("\n" + "=" * 70)
    print("\n💡 Use these thresholds in update_readme_stats.py and CI/CD workflows.")
    print("⚠️  Thresholds are conservative (P95 + 20% safety margin).")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate performance thresholds from baseline measurements"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT,
        help="Directory containing baseline JSON files (default: project root)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "performance_thresholds.json",
        help="Output JSON file path (default: performance_thresholds.json)",
    )
    parser.add_argument(
        "--safety-margin",
        type=float,
        default=0.20,
        help="Safety margin as decimal (default: 0.20 = 20%%)",
    )
    args = parser.parse_args()

    try:
        print("🔍 Loading baseline measurements...")
        baselines = load_baseline_files(args.input_dir)
        print(f"   Loaded {len(baselines)} baseline files")

        print("\n📊 Aggregating statistics...")
        aggregated = aggregate_operation_stats(baselines)
        print(f"   Analyzed {len(aggregated)} operations")

        print("\n🎯 Calculating thresholds...")
        thresholds = calculate_thresholds(aggregated, args.safety_margin)

        save_thresholds(thresholds, args.output)
        print_thresholds(thresholds)

        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
