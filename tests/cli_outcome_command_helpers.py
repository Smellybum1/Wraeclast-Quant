from __future__ import annotations

from pathlib import Path


def record_outcome_args(
    database_path: Path,
    *,
    run_id: int = 1,
    item_name: str = "Stormglass Catalyst",
    outcome: str = "positive",
    notes: str | None = None,
) -> list[str]:
    args = [
        "record-outcome",
        "--database-path",
        str(database_path),
        "--run-id",
        str(run_id),
        "--item-name",
        item_name,
        "--outcome",
        outcome,
    ]
    if notes is not None:
        args.extend(["--notes", notes])
    return args


def outcomes_args(database_path: Path) -> list[str]:
    return ["outcomes", "--database-path", str(database_path)]


def review_queue_args(
    database_path: Path,
    *,
    run_id: int | None = None,
    output_path: Path | None = None,
    context_path: Path | None = None,
) -> list[str]:
    args = ["review-queue", "--database-path", str(database_path)]
    if run_id is not None:
        args.extend(["--run-id", str(run_id)])
    if output_path is not None:
        args.extend(["--output-path", str(output_path)])
    if context_path is not None:
        args.extend(["--context-path", str(context_path)])
    return args


def review_coverage_args(database_path: Path, *, run_id: int | None = None) -> list[str]:
    args = ["review-coverage", "--database-path", str(database_path)]
    if run_id is not None:
        args.extend(["--run-id", str(run_id)])
    return args


def outcome_review_args(database_path: Path) -> list[str]:
    return ["outcome-review", "--database-path", str(database_path)]


def outcome_report_args(database_path: Path, output_path: Path) -> list[str]:
    return [
        "outcome-report",
        "--database-path",
        str(database_path),
        "--output-path",
        str(output_path),
    ]


def calibration_report_args(database_path: Path, output_path: Path) -> list[str]:
    return [
        "calibration-report",
        "--database-path",
        str(database_path),
        "--output-path",
        str(output_path),
    ]


def calibration_args(database_path: Path) -> list[str]:
    return ["calibration", "--database-path", str(database_path)]


__all__ = [
    "calibration_args",
    "calibration_report_args",
    "outcome_review_args",
    "outcome_report_args",
    "outcomes_args",
    "record_outcome_args",
    "review_coverage_args",
    "review_queue_args",
]
