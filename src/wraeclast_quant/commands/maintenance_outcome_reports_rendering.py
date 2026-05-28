from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.review_guidance import calibration_prompt_next_action
from wraeclast_quant.reports.outcome_guidance import (
    local_report_next_action,
    no_outcome_review_lines,
)
from wraeclast_quant.storage.models import OutcomeReviewRecord
from wraeclast_quant.storage.repositories import ALLOWED_OUTCOMES

console = Console(width=260)


def print_no_outcome_reviews() -> None:
    console.print("\n".join(line for line in no_outcome_review_lines() if line))


def print_outcome_review(
    records: list[OutcomeReviewRecord],
    summary_by_action: dict[str, dict[str, int]],
    calibration_prompts: list[str] | None = None,
) -> None:
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

    summary_table = Table(title="Outcome Review By Action")
    summary_table.add_column("Action")
    for label in sorted(ALLOWED_OUTCOMES):
        summary_table.add_column(label, justify="right")
    for action, counts in sorted(summary_by_action.items()):
        summary_table.add_row(
            action,
            *(str(counts.get(label, 0)) for label in sorted(ALLOWED_OUTCOMES)),
        )
    console.print(summary_table)
    if calibration_prompts:
        console.print(calibration_prompt_next_action(len(calibration_prompts)))
    console.print(outcome_review_next_action())


def outcome_review_next_action() -> str:
    return (
        "Next: run wq calibration for read-only score/action summaries, "
        "or wq outcome-report --output-path data/processed/outcome_review.md "
        "to write a local Markdown report."
    )


def print_outcome_report_written(written_path: Path, *, has_reviews: bool) -> None:
    console.print(outcome_report_written_message(written_path, has_reviews=has_reviews))
    console.print(local_report_next_action())


def outcome_report_written_message(written_path: Path, *, has_reviews: bool) -> str:
    if not has_reviews:
        return f"Wrote empty outcome review report to {written_path}"
    return f"Wrote outcome review report to {written_path}"
