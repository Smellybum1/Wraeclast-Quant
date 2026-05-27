from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.review_queue_commands import (
    OUTCOME_DECISIONS_PATH,
    record_outcomes_dry_run_command,
    review_queue_decisions_template_command,
    review_queue_worksheet_command,
)
from wraeclast_quant.reports.review_queue_worksheet import (
    local_review_caveat,
    outcome_label_guide,
    record_outcome_command,
)
from wraeclast_quant.storage.models import ReviewCoverageRecord, StoredOpportunityRecord

console = Console(width=260)


def print_no_snapshots() -> None:
    console.print("No snapshots found.")


def print_no_unreviewed_recommendations(run_id: int) -> None:
    console.print(f"No unreviewed recommendations found for run #{run_id}.")


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
    console.print(_batch_review_next_steps(run_id))
    console.print(_record_outcome_command_templates(run_id, opportunities))


def print_review_coverage(run_id: int, source_mode: str, coverage: ReviewCoverageRecord) -> None:
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
        console.print(_batch_review_next_steps(run_id))


def _record_outcome_command_templates(
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
) -> str:
    lines = ["Suggested review commands:"]
    for opportunity in opportunities:
        lines.append(f"  {record_outcome_command(run_id, opportunity.item_name)}")
    return "\n".join(lines)


def _batch_review_next_steps(run_id: int) -> str:
    return "\n".join(
        [
            "Batch review next steps:",
            f"  {review_queue_worksheet_command(run_id)}",
            f"  {review_queue_decisions_template_command(run_id)}",
            f"  Fill outcome labels in {OUTCOME_DECISIONS_PATH}.",
            f"  {record_outcomes_dry_run_command()}",
        ]
    )
