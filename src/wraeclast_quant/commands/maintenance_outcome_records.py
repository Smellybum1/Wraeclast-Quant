from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES, SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("record-outcome")
    def record_outcome(
        run_id: int = typer.Option(..., "--run-id", min=1, help="Analysis run id."),
        item_name: str = typer.Option(..., "--item-name", help="Item name from the analysis run."),
        outcome: str = typer.Option(..., "--outcome", help="positive, neutral, or negative."),
        notes: str = typer.Option("", "--notes", help="Optional local review notes."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        repository = SnapshotRepository(database_path)
        try:
            record = repository.save_recommendation_outcome(
                run_id=run_id,
                item_name=item_name,
                outcome=outcome,
                notes=notes,
            )
        except ValueError as error:
            raise typer.BadParameter(str(error)) from error

        console.print(
            f"Recorded {record.outcome} outcome for '{record.item_name}' from run #{record.run_id}."
        )

    @app.command()
    def outcomes(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        records = repository.list_recent_outcomes(limit=limit)
        if not records:
            console.print("No recommendation outcomes recorded.")
            return

        table = Table(title="Recommendation Outcomes")
        table.add_column("Run", justify="right")
        table.add_column("Item")
        table.add_column("Outcome")
        table.add_column("Observed")
        table.add_column("Notes")
        for record in records:
            table.add_row(
                str(record.run_id),
                record.item_name,
                record.outcome,
                record.observed_at,
                record.notes,
            )
        console.print(table)

        summary = repository.outcome_summary()
        summary_table = Table(title="Outcome Summary")
        summary_table.add_column("Outcome")
        summary_table.add_column("Count", justify="right")
        for label in sorted(ALLOWED_OUTCOMES):
            summary_table.add_row(label, str(summary.get(label, 0)))
        console.print(summary_table)
