"""Evaluation runner placeholder for the natural language task set."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import csv
import json
from collections import Counter
from typing import Any

from run_demo import run_task


def load_tasks(task_file: str | Path) -> list[dict[str, Any]]:
    """Load evaluation tasks from a JSON file."""

    with Path(task_file).open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_tasks(
    tasks: list[dict[str, Any]],
    output_dir: str | Path = "outputs/eval",
    results_path: str | Path = "outputs/results.csv",
) -> list[dict[str, Any]]:
    """Run all tasks and write a summary CSV."""

    output_dir = Path(output_dir)
    results_path = Path(results_path)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []

    for task in tasks:
        task_id = task["task_id"]
        task_output_dir = output_dir / task_id
        task_output_dir.mkdir(parents=True, exist_ok=True)

        try:
            result = run_task(
                task=task["instruction"],
                output_dir=str(task_output_dir),
                planner=task.get("planner", "rule"),
                missing_targets=task.get("missing_targets", []),
            )
        except Exception as exc:
            result = {
                "success": False,
                "duration": 0.0,
                "final_position_error": "",
                "failure_reason": f"evaluation_exception:{type(exc).__name__}",
            }

        rows.append(
            {
                "task_id": task_id,
                "instruction": task["instruction"],
                "success": result["success"],
                "duration": round(float(result["duration"]), 4),
                "final_position_error": result["final_position_error"],
                "failure_reason": result["failure_reason"],
                "planner": result.get("planner", task.get("planner", "rule")),
                "planner_fallback_reason": result.get("planner_fallback_reason", ""),
            }
        )

    write_results(rows, results_path)
    print_summary(rows)
    return rows


def write_results(rows: list[dict[str, Any]], results_path: Path) -> None:
    """Write evaluation rows to CSV."""

    fieldnames = [
        "task_id",
        "instruction",
        "success",
        "duration",
        "final_position_error",
        "failure_reason",
        "planner",
        "planner_fallback_reason",
    ]

    with results_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows: list[dict[str, Any]]) -> None:
    """Print aggregate evaluation statistics."""

    total = len(rows)
    successes = [row for row in rows if row["success"] is True]
    success_rate = len(successes) / total if total else 0.0

    durations = [float(row["duration"]) for row in rows]
    avg_duration = sum(durations) / len(durations) if durations else 0.0

    errors = [
        float(row["final_position_error"])
        for row in successes
        if row["final_position_error"] not in ("", None)
    ]
    avg_error = sum(errors) / len(errors) if errors else 0.0

    failure_reasons = Counter(
        row["failure_reason"] or "success"
        for row in rows
        if row["success"] is not True
    )

    print(f"Total tasks: {total}")
    print(f"Success rate: {success_rate:.2%}")
    print(f"Average duration: {avg_duration:.3f}s")
    print(f"Average final position error on success: {avg_error:.4f}m")
    print("Failure reasons:")
    for reason, count in failure_reasons.items():
        print(f"  - {reason}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the VLA drone agent task set.")
    parser.add_argument("--task-file", default="experiments/tasks.json")
    parser.add_argument("--output-dir", default="outputs/eval")
    parser.add_argument("--results-path", default="outputs/results.csv")
    args = parser.parse_args()

    tasks = load_tasks(args.task_file)
    evaluate_tasks(tasks, output_dir=args.output_dir, results_path=args.results_path)


if __name__ == "__main__":
    main()