from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands.intake_rendering import console, print_opportunities
from wraeclast_quant.importers.manual import SIGNAL_FIELDS, ManualImportError, load_manual_items
from wraeclast_quant.importers.summary import summarize_opportunities
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command("import")
    def import_data(
        input_path: Path = typer.Option(..., "--input-path", help="Local JSON or CSV signal file."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        try:
            items = load_manual_items(input_path)
        except ManualImportError as error:
            raise typer.BadParameter(str(error)) from error

        opportunities = rank_opportunities(items)
        print_opportunities("Imported Opportunities", opportunities)
        repository = SnapshotRepository(database_path)
        run = repository.create_analysis_run(
            source_mode="manual-import",
            item_count=len(opportunities),
        )
        repository.save_scored_opportunities(run.id, opportunities)
        console.print(f"Recorded manual import run #{run.id} to {database_path}")

    @app.command("validate-import")
    def validate_import(
        input_path: Path = typer.Option(..., "--input-path", help="Local JSON or CSV signal file."),
    ) -> None:
        try:
            items = load_manual_items(input_path)
        except ManualImportError as error:
            raise typer.BadParameter(str(error)) from error

        opportunities = rank_opportunities(items)
        print_opportunities("Manual Import Validation", opportunities)
        console.print(f"Valid manual import: {len(opportunities)} items.")

    @app.command("inspect-import")
    def inspect_import(
        input_path: Path = typer.Option(..., "--input-path", help="Local JSON or CSV signal file."),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
    ) -> None:
        try:
            items = load_manual_items(input_path)
        except ManualImportError as error:
            raise typer.BadParameter(str(error)) from error

        opportunities = rank_opportunities(items)
        summary = summarize_opportunities(opportunities)

        overview = Table(title="Manual Import Diagnostics")
        overview.add_column("Metric")
        overview.add_column("Value", justify="right")
        overview.add_row("Items", str(summary.item_count))
        overview.add_row("Average score", f"{summary.average_score:.2f}")
        overview.add_row("Minimum score", f"{summary.min_score:.2f}")
        overview.add_row("Maximum score", f"{summary.max_score:.2f}")
        for action, count in summary.action_counts.items():
            overview.add_row(f"{action} count", str(count))
        console.print(overview)

        signals = Table(title="Signal Averages")
        signals.add_column("Signal")
        signals.add_column("Average", justify="right")
        for field in SIGNAL_FIELDS:
            signals.add_row(field, f"{summary.signal_averages[field]:.2f}")
        console.print(signals)

        print_opportunities("Top Imported Opportunities", opportunities[:limit])
        console.print("Inspect import is read-only. No snapshots, reports, exports, or databases were written.")
