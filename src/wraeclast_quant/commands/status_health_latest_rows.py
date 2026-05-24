from __future__ import annotations

from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row
from wraeclast_quant.commands.status_health_storage import latest_run_empty_details


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
            (
                f"{context.coverage.reviewed_recommendations}/"
                f"{context.coverage.total_recommendations} reviewed; "
                f"{context.coverage.reviewed_percent:.1f}%; "
                f"{context.coverage.unreviewed_recommendations} unreviewed"
            ),
        )
