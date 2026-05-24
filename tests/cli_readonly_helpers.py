from __future__ import annotations

from pathlib import Path


def read_only_missing_database_command_cases(tmp_path: Path) -> list[tuple[list[str], str]]:
    return [
        (["snapshots"], "No snapshots found."),
        (["compare"], "No snapshots found."),
        (["alerts"], "No snapshots found."),
        (["export", "--output-path", str(tmp_path / "public_intel.json")], "No snapshots found."),
        (["outcomes"], "No recommendation outcomes recorded."),
        (["review-queue"], "No snapshots found."),
        (["review-coverage"], "No snapshots found."),
        (["outcome-review"], "No reviewed recommendation outcomes found."),
        (
            ["outcome-report", "--output-path", str(tmp_path / "outcome_review.md")],
            "Wrote empty outcome review report",
        ),
    ]


__all__ = ["read_only_missing_database_command_cases"]
