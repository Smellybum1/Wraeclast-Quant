from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands.snapshot_formatting import hidden_snapshot_items_text
from wraeclast_quant.commands.snapshot_rendering import console
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command()
    def snapshots(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(5, "--limit", min=1, max=25),
    ) -> None:
        repository = SnapshotRepository(database_path)
        recent_runs = repository.list_recent_runs(limit=limit)
        if not recent_runs:
            console.print("No snapshots found.")
            return

        runs_table = Table(title="Recent Analysis Runs")
        runs_table.add_column("Run", justify="right")
        runs_table.add_column("Created")
        runs_table.add_column("Source")
        runs_table.add_column("Items", justify="right")
        for run in recent_runs:
            runs_table.add_row(str(run.id), run.created_at, run.source_mode, str(run.item_count))
        console.print(runs_table)

        latest = recent_runs[0]
        opportunities = repository.scored_opportunities_for_run(latest.id, limit=limit)
        items_table = Table(title=f"Top Items From Run #{latest.id}")
        items_table.add_column("Item")
        items_table.add_column("Score", justify="right")
        items_table.add_column("Action")
        for opportunity in opportunities:
            items_table.add_row(
                opportunity.item_name,
                f"{opportunity.opportunity_score:.2f}",
                opportunity.action,
            )
        console.print(items_table)
        hidden_items = hidden_snapshot_items_text(
            displayed_count=len(opportunities),
            total_count=latest.item_count,
        )
        if hidden_items is not None:
            console.print(hidden_items)
