from __future__ import annotations

import sqlite3
from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_outcome_batch_decisions import (
    load_batch_outcome_decisions,
    validate_batch_outcome_decisions,
)
from wraeclast_quant.commands.maintenance_outcome_records_rendering import (
    batch_outcome_dry_run_success_message,
    batch_outcome_record_success_message,
    batch_outcome_write_error_message,
    post_outcome_record_next_steps,
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

    @app.command("record-outcomes")
    def record_outcomes(
        input_path: Path = typer.Option(
            ...,
            "--input-path",
            help="Local JSON file with run_id and human-reviewed outcome decisions.",
        ),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Validate the local outcome batch without writing records.",
        ),
    ) -> None:
        repository = SnapshotRepository(database_path)
        try:
            run_id, decisions = load_batch_outcome_decisions(input_path)
            validate_batch_outcome_decisions(repository, run_id, decisions)
            if dry_run:
                typer.echo(
                    batch_outcome_dry_run_success_message(
                        len(decisions),
                        run_id,
                        input_path,
                    )
                )
                return
            try:
                records = repository.save_recommendation_outcome_batch(run_id, decisions)
            except sqlite3.Error as error:
                typer.echo(batch_outcome_write_error_message(error), err=True)
                raise typer.Exit(code=1) from error
        except ValueError as error:
            raise typer.BadParameter(str(error)) from error

        typer.echo(batch_outcome_record_success_message(len(records), run_id, input_path))
        typer.echo(post_outcome_record_next_steps(run_id))

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
