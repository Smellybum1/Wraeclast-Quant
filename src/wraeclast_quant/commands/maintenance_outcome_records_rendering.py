from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.models import RecommendationOutcomeRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES

console = Console(width=260)


def print_outcome_record(record: RecommendationOutcomeRecord) -> None:
    console.print(f"Recorded {record.outcome} outcome for '{record.item_name}' from run #{record.run_id}.")


def print_recent_outcomes(
    records: list[RecommendationOutcomeRecord],
    summary: dict[str, int],
) -> None:
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

    summary_table = Table(title="Outcome Summary")
    summary_table.add_column("Outcome")
    summary_table.add_column("Count", justify="right")
    for label in sorted(ALLOWED_OUTCOMES):
        summary_table.add_row(label, str(summary.get(label, 0)))
    console.print(summary_table)


def print_no_outcomes() -> None:
    console.print("No recommendation outcomes recorded.")
