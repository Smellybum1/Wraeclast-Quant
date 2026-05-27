from __future__ import annotations

from rich.console import Console
from rich.table import Table

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
    console.print(_local_review_caveat(source_mode))
    console.print(_outcome_label_guide())
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
    console.print(_local_review_caveat(source_mode))
    console.print(_outcome_label_guide())
    if coverage.unreviewed_recommendations:
        console.print(f"Next: run wq review-queue --run-id {run_id} to see item-specific review commands.")


def _local_review_caveat(source_mode: str) -> str:
    return (
        f"Run source: {source_mode}. Review outcomes are local decision-support only; "
        "no trades, whispers, gameplay, publishing, or live collection are performed."
    )


def _outcome_label_guide() -> str:
    return (
        "Outcome labels: positive=useful signal, neutral=mixed or unclear, "
        "negative=not useful after review."
    )


def _record_outcome_command_templates(
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
) -> str:
    lines = ["Suggested review commands:"]
    for opportunity in opportunities:
        lines.append(
            "  wq record-outcome "
            f"--run-id {run_id} "
            f'--item-name "{_powershell_double_quoted_text(opportunity.item_name)}" '
            "--outcome positive|neutral|negative"
        )
    return "\n".join(lines)


def _powershell_double_quoted_text(value: str) -> str:
    return value.replace("`", "``").replace('"', '`"')
