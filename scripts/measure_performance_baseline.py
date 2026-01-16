#!/usr/bin/env python3
"""Measure performance baselines for documentation update operations.

This script measures the time taken for various documentation-related operations
to establish realistic performance thresholds. Run this for at least 7 days to
capture variations due to system load, CI/CD conditions, etc.

Usage:
    python scripts/measure_performance_baseline.py
    python scripts/measure_performance_baseline.py --iterations 10
    python scripts/measure_performance_baseline.py --output baselines_custom.json
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent


def measure_operation(  # noqa: C901
    operation_name: str,
    command: list[str],
    iterations: int = 10,
    verbose: bool = False,
) -> dict[str, Any]:
    """Measure the time taken for an operation across multiple iterations.

    Args:
        operation_name: Human-readable name for the operation
        command: Command to execute as list of strings
        iterations: Number of times to run the operation
        verbose: Print detailed progress

    Returns:
        Dictionary with timing statistics
    """
    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Measuring: {operation_name}")
        print(f"Command: {' '.join(command)}")
        print(f"Iterations: {iterations}")
        print(f"{'=' * 60}")

    durations = []

    for i in range(iterations):
        if verbose:
            print(f"  Iteration {i + 1}/{iterations}...", end=" ", flush=True)

        start_time = time.perf_counter()
        try:
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False,
            )
            end_time = time.perf_counter()
            duration = end_time - start_time

            if result.returncode == 0:
                durations.append(duration)
                if verbose:
                    print(f"✓ {duration:.2f}s")
            elif verbose:
                print(f"✗ Failed (exit code {result.returncode})")
                # Continue even if some iterations fail
        except subprocess.TimeoutExpired:
            if verbose:
                print("✗ Timeout (>300s)")
        except Exception as e:
            if verbose:
                print(f"✗ Error: {e}")

    if not durations:
        return {
            "operation": operation_name,
            "command": " ".join(command),
            "iterations_attempted": iterations,
            "iterations_successful": 0,
            "error": "All iterations failed",
        }

    # Calculate statistics
    stats = {
        "operation": operation_name,
        "command": " ".join(command),
        "iterations_attempted": iterations,
        "iterations_successful": len(durations),
        "min": min(durations),
        "max": max(durations),
        "mean": statistics.mean(durations),
        "median": statistics.median(durations),
        "stdev": statistics.stdev(durations) if len(durations) > 1 else 0,
        "p95": sorted(durations)[int(len(durations) * 0.95)]
        if len(durations) >= 20
        else max(durations),
        "p99": sorted(durations)[int(len(durations) * 0.99)]
        if len(durations) >= 100
        else max(durations),
        "all_durations": durations,
    }

    if verbose:
        print("\n  Results:")
        print(f"    Successful: {stats['iterations_successful']}/{iterations}")
        print(f"    Min:    {stats['min']:.2f}s")
        print(f"    Mean:   {stats['mean']:.2f}s")
        print(f"    Median: {stats['median']:.2f}s")
        print(f"    Max:    {stats['max']:.2f}s")
        print(f"    StdDev: {stats['stdev']:.2f}s")
        print(f"    P95:    {stats['p95']:.2f}s")

    return stats


def measure_all_operations(iterations: int = 10, verbose: bool = False) -> dict[str, Any]:
    """Measure all documentation-related operations.

    Args:
        iterations: Number of iterations per operation
        verbose: Print detailed progress

    Returns:
        Dictionary with all measurements and metadata
    """
    print("🔍 Starting performance baseline measurements...")
    print(f"Date: {datetime.now(UTC).isoformat()}")
    print(f"Iterations per operation: {iterations}")
    print()

    operations = [
        {
            "name": "Test Coverage",
            "command": ["uv", "run", "pytest", "--cov=app", "--cov-report=term", "--quiet"],
        },
        {
            "name": "MyPy Type Check",
            "command": ["uv", "run", "mypy", "app/", "--strict", "--no-error-summary"],
        },
        {
            "name": "Interrogate Docstrings",
            "command": ["uv", "run", "interrogate", "-c", "pyproject.toml", "--quiet"],
        },
        {
            "name": "Test Collection Only",
            "command": ["uv", "run", "pytest", "--collect-only", "--quiet"],
        },
        {
            "name": "Ruff Lint Check",
            "command": ["uv", "run", "ruff", "check", "app/"],
        },
    ]

    results = {
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "iterations_per_operation": iterations,
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
        },
        "operations": {},
    }

    for op in operations:
        stats = measure_operation(
            op["name"],
            op["command"],
            iterations=iterations,
            verbose=verbose,
        )
        results["operations"][op["name"]] = stats

    # Calculate total simulated update time (parallel operations use max, not sum)
    successful_ops = [
        v for v in results["operations"].values() if v.get("iterations_successful", 0) > 0
    ]

    if successful_ops:
        # In parallel execution, total time is dominated by the longest operation
        # plus some overhead for coordination
        parallel_p95 = max(op["p95"] for op in successful_ops) + 5  # 5s overhead

        results["summary"] = {
            "total_operations": len(operations),
            "successful_operations": len(successful_ops),
            "failed_operations": len(operations) - len(successful_ops),
            "estimated_parallel_p95": parallel_p95,
            "recommended_timeout": int(parallel_p95 * 1.5),  # 50% safety margin
        }

    return results


def save_results(results: dict[str, Any], output_file: Path) -> None:
    """Save measurement results to JSON file.

    Args:
        results: Measurement results dictionary
        output_file: Path to output JSON file
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Results saved to: {output_file}")


def print_summary(results: dict[str, Any]) -> None:
    """Print a summary of the measurement results.

    Args:
        results: Measurement results dictionary
    """
    print("\n" + "=" * 60)
    print("PERFORMANCE BASELINE SUMMARY")
    print("=" * 60)

    summary = results.get("summary", {})

    print(
        f"\nOperations Measured: {summary.get('successful_operations', 0)}/{summary.get('total_operations', 0)}"
    )

    if summary.get("estimated_parallel_p95"):
        print("\nEstimated Parallel Execution Time (P95):")
        print(f"  {summary['estimated_parallel_p95']:.1f}s")
        print("\nRecommended Timeout (P95 + 50% margin):")
        print(f"  {summary['recommended_timeout']}s")

    print("\nOperation Details:")
    for op_name, op_data in results.get("operations", {}).items():
        if op_data.get("iterations_successful", 0) > 0:
            print(f"\n  {op_name}:")
            print(f"    Mean: {op_data['mean']:.2f}s")
            print(f"    P95:  {op_data['p95']:.2f}s")
        else:
            print(f"\n  {op_name}: ❌ Failed")

    print("\n" + "=" * 60)
    print("\n📊 Run this script daily for 7 days to establish reliable baselines.")
    print("💡 After 7 days, use calculate_thresholds.py to set performance thresholds.")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Measure performance baselines for documentation operations"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations per operation (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "performance_baselines.json",
        help="Output JSON file path (default: performance_baselines.json)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed progress",
    )
    args = parser.parse_args()

    try:
        results = measure_all_operations(
            iterations=args.iterations,
            verbose=args.verbose,
        )

        save_results(results, args.output)
        print_summary(results)

        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Measurement interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
