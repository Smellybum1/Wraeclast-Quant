from __future__ import annotations

from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row
from wraeclast_quant.commands.status_health_storage import latest_run_empty_details
from wraeclast_quant.reports.review_queue_commands import batch_outcome_review_next_action
from wraeclast_quant.storage.models import ReviewCoverageRecord


def add_latest_run_rows(
    status_rows: list[dict[str, str]],
    context: StatusHealthContext,
) -> None:
    if context.latest is None:
        add_status_row(status_rows, "Latest run", "none", latest_run_empty_details(context.database_health))
        add_status_row(status_rows, "Review coverage", "none", "No latest run.")
        return

    add_status_row(
        status_rows,
        "Latest run",
        "ok",
        (
            f"#{context.latest.id} {context.latest.source_mode}; "
            f"{context.latest.item_count} items; {context.latest.created_at}"
        ),
    )
    if context.coverage is not None:
        add_status_row(
            status_rows,
            "Review coverage",
            "ok",
            review_coverage_details(context.coverage),
        )


def review_coverage_details(coverage: ReviewCoverageRecord) -> str:
    details = (
        f"{coverage.reviewed_recommendations}/"
        f"{coverage.total_recommendations} reviewed; "
        f"{coverage.reviewed_percent:.1f}%; "
        f"{coverage.unreviewed_recommendations} unreviewed"
    )
    if coverage.unreviewed_recommendations:
        return (
            f"{details}; next: {batch_outcome_review_next_action(coverage.run_id)}"
        )
    return f"{details}; all recommendations reviewed"
