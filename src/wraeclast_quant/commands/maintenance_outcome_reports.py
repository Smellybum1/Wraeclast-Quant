from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.outcome_review import (
    DEFAULT_OUTCOME_REVIEW_PATH,
    write_outcome_review,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES, SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("outcome-review")
    def outcome_review(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        records = repository.list_outcome_reviews(limit=limit)
        if not records:
            console.print("No reviewed recommendation outcomes found.")
            return

        table = Table(title="Recommendation Outcome Review")
        table.add_column("Run", justify="right")
        table.add_column("Item")
        table.add_column("Score", justify="right")
        table.add_column("Action")
        table.add_column("Outcome")
        table.add_column("Observed")
        table.add_column("Notes")
        for record in records:
            table.add_row(
                str(record.run_id),
                record.item_name,
                f"{record.opportunity_score:.2f}",
                record.action,
                record.outcome,
                record.observed_at,
                record.notes,
            )
        console.print(table)

        summary = repository.outcome_review_summary_by_action()
        summary_table = Table(title="Outcome Review By Action")
        summary_table.add_column("Action")
        for label in sorted(ALLOWED_OUTCOMES):
            summary_table.add_column(label, justify="right")
        for action, counts in sorted(summary.items()):
            summary_table.add_row(
                action,
                *(str(counts.get(label, 0)) for label in sorted(ALLOWED_OUTCOMES)),
            )
        console.print(summary_table)

    @app.command("outcome-report")
    def outcome_report(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        output_path: Path = typer.Option(DEFAULT_OUTCOME_REVIEW_PATH, "--output-path"),
        limit: int = typer.Option(20, "--limit", min=1, max=100),
    ) -> None:
        repository = SnapshotRepository(database_path)
        reviews = repository.list_outcome_reviews(limit=limit)
        written_path = write_outcome_review(
            reviews=reviews,
            summary_by_action=repository.outcome_review_summary_by_action(),
            path=output_path,
        )
        if not reviews:
            console.print(f"Wrote empty outcome review report to {written_path}")
            return
        console.print(f"Wrote outcome review report to {written_path}")
