from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.importers.manual import SIGNAL_FIELDS, ManualImportError, load_manual_items
from wraeclast_quant.importers.summary import summarize_opportunities
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.reports.watchlist import top_watchlist
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def analyze(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        opportunities = _sample_opportunities(sample_data)
        _print_opportunities("Scored Opportunities", opportunities)
        run = _record_analysis_run(database_path, opportunities)
        console.print(f"Recorded analysis run #{run.id} to {database_path}")

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
        _print_opportunities("Imported Opportunities", opportunities)
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
        _print_opportunities("Manual Import Validation", opportunities)
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

        _print_opportunities("Top Imported Opportunities", opportunities[:limit])
        console.print("Inspect import is read-only. No snapshots, reports, exports, or databases were written.")

    @app.command()
    def watchlist() -> None:
        opportunities = top_watchlist(rank_opportunities(SAMPLE_ITEMS))
        table = Table(title="Watchlist")
        table.add_column("Item")
        table.add_column("Score", justify="right")
        table.add_column("Action")
        for opportunity in opportunities:
            table.add_row(
                opportunity.item_name,
                f"{opportunity.opportunity_score:.2f}",
                opportunity.action,
            )
        console.print(table)


def _sample_opportunities(sample_data: bool):
    if not sample_data:
        raise typer.BadParameter("Only --sample-data is supported in the MVP.")
    return rank_opportunities(SAMPLE_ITEMS)


def _record_analysis_run(database_path: Path, opportunities):
    repository = SnapshotRepository(database_path)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    return run


def _print_opportunities(title: str, opportunities) -> None:
    table = Table(title=title)
    table.add_column("Item")
    table.add_column("Score", justify="right")
    table.add_column("Action")
    for opportunity in opportunities:
        table.add_row(
            opportunity.item_name,
            f"{opportunity.opportunity_score:.2f}",
            opportunity.action,
        )
    console.print(table)
