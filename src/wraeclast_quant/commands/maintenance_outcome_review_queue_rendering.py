from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.review_queue_commands import (
    batch_outcome_review_steps,
    record_outcome_command_templates,
)
from wraeclast_quant.reports.review_guidance import calibration_prompt_next_action
from wraeclast_quant.reports.review_queue_worksheet import (
    local_review_caveat,
    outcome_label_guide,
)
from wraeclast_quant.storage.models import ReviewCoverageRecord, StoredOpportunityRecord

console = Console(width=260)


def print_no_snapshots() -> None:
    console.print("No snapshots found.")


def print_no_unreviewed_recommendations(
    run_id: int,
    calibration_prompts: list[str] | None = None,
) -> None:
    console.print(f"No unreviewed recommendations found for run #{run_id}.")
    if calibration_prompts:
        console.print(calibration_prompt_next_action(len(calibration_prompts)))


def print_review_queue(
    run_id: int,
    source_mode: str,
    opportunities: list[StoredOpportunityRecord],
) -> None:
    table = Table(title=f"Recommendation Review Queue - Run #{run_id} ({source_mode})")
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
    console.print(local_review_caveat(source_mode))
    console.print(outcome_label_guide())
    console.print(batch_outcome_review_steps(run_id))
    console.print(
        record_outcome_command_templates(
            run_id,
            [opportunity.item_name for opportunity in opportunities],
        )
    )


def print_review_coverage(
    run_id: int,
    source_mode: str,
    coverage: ReviewCoverageRecord,
    calibration_prompts: list[str] | None = None,
) -> None:
    table = Table(title=f"Recommendation Review Coverage - Run #{run_id} ({source_mode})")
    table.add_column("Total", justify="right")
    table.add_column("Reviewed", justify="right")
    table.add_column("Unreviewed", justify="right")
    table.add_column("Reviewed %", justify="right")
    table.add_row(
        str(coverage.total_recommendations),
        str(coverage.reviewed_recommendations),
        str(coverage.unreviewed_recommendations),
        f"{coverage.reviewed_percent:.1f}%",
    )
    console.print(table)
    console.print(local_review_caveat(source_mode))
    console.print(outcome_label_guide())
    if coverage.unreviewed_recommendations:
        console.print(batch_outcome_review_steps(run_id))
    elif calibration_prompts:
        console.print(calibration_prompt_next_action(len(calibration_prompts)))
