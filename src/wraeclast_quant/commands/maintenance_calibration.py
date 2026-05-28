from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_calibration_rendering import (
    console,
    print_calibration_report_written,
    print_calibration_tables,
)
from wraeclast_quant.reports.calibration import (
    DEFAULT_CALIBRATION_REPORT_PATH,
    build_calibration,
    write_calibration_report,
)
from wraeclast_quant.reports.outcome_guidance import no_outcome_review_lines
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command()
    def calibration(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        result = build_calibration(SnapshotRepository(database_path), limit=limit)
        if not result.has_outcomes:
            console.print("\n".join(line for line in no_outcome_review_lines() if line))
            return

        print_calibration_tables(result)
        console.print(
            "Calibration is local-only and read-only. It did not change scoring weights or thresholds."
        )
        console.print(
            "Next: run wq calibration-report --output-path data/processed/calibration_report.md "
            "to write the local Markdown calibration artifact."
        )

    @app.command("calibration-report")
    def calibration_report(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        output_path: Path = typer.Option(DEFAULT_CALIBRATION_REPORT_PATH, "--output-path"),
        limit: int = typer.Option(50, "--limit", min=1, max=100),
    ) -> None:
        result = build_calibration(SnapshotRepository(database_path), limit=limit)
        written_path = write_calibration_report(result, output_path)
        print_calibration_report_written(written_path, has_outcomes=result.has_outcomes)
