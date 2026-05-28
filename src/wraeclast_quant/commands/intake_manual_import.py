from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.intake_rendering import console, print_opportunities
from wraeclast_quant.commands.intake_manual_import_rendering import (
    manual_import_daily_next_action,
    manual_import_validate_next_action,
    print_manual_import_diagnostics,
)
from wraeclast_quant.commands.intake_manual_import_workflow import (
    load_manual_opportunities,
    record_manual_import_run,
    summarize_manual_opportunities,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command("import")
    def import_data(
        input_path: Path = typer.Option(..., "--input-path", help="Local JSON or CSV signal file."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        opportunities = load_manual_opportunities(input_path)
        print_opportunities("Imported Opportunities", opportunities)
        run = record_manual_import_run(database_path, opportunities)
        console.print(f"Recorded manual import run #{run.id} to {database_path}")

    @app.command("validate-import")
    def validate_import(
        input_path: Path = typer.Option(..., "--input-path", help="Local JSON or CSV signal file."),
    ) -> None:
        opportunities = load_manual_opportunities(input_path)
        print_opportunities("Manual Import Validation", opportunities)
        console.print(f"Valid manual import: {len(opportunities)} items.")
        console.print(manual_import_daily_next_action(input_path))

    @app.command("inspect-import")
    def inspect_import(
        input_path: Path = typer.Option(..., "--input-path", help="Local JSON or CSV signal file."),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
    ) -> None:
        opportunities = load_manual_opportunities(input_path)
        summary = summarize_manual_opportunities(opportunities)

        print_manual_import_diagnostics(summary, opportunities, limit)
        console.print("Inspect import is read-only. No snapshots, reports, exports, or databases were written.")
        console.print(manual_import_validate_next_action(input_path))
