from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_outcome_records_rendering import (
    print_no_outcomes,
    print_outcome_record,
    print_recent_outcomes,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


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

        print_outcome_record(record)

    @app.command()
    def outcomes(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        records = repository.list_recent_outcomes(limit=limit)
        if not records:
            print_no_outcomes()
            return

        summary = repository.outcome_summary()
        print_recent_outcomes(records, summary)
