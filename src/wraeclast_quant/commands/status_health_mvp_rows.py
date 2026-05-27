from __future__ import annotations

from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row
from wraeclast_quant.reports.review_queue_commands import status_outcome_review_next_action


NEXT_MANUAL_OBSERVATION_ACTION = (
    "next: wq currency-exchange-manual-snapshot --input-path <current-snapshot>; "
    "then follow docs/MVP_DAILY_WORKFLOW.md to create <manual-import-output> "
    "and run wq daily --input-path <manual-import-output>."
)


def add_mvp_readiness_row(
    status_rows: list[dict[str, str]],
    context: StatusHealthContext,
) -> None:
    add_status_row(
        status_rows,
        "MVP readiness",
        mvp_readiness_status(context),
        mvp_readiness_details(context),
    )


def mvp_readiness_status(context: StatusHealthContext) -> str:
    if context.latest is None:
        return "none"
    return "ok"


def mvp_readiness_details(context: StatusHealthContext) -> str:
    if context.latest is None:
        return f"No local run yet; {NEXT_MANUAL_OBSERVATION_ACTION}"

    run_summary = f"No-OAuth local loop ready on run #{context.latest.id}"
    if context.coverage is None:
        return f"{run_summary}; next: wq review-queue."

    reviewed = (
        f"{context.coverage.reviewed_recommendations}/"
        f"{context.coverage.total_recommendations} reviewed"
    )
    if context.coverage.unreviewed_recommendations:
        return (
            f"{run_summary}; {reviewed}; next: "
            f"{status_outcome_review_next_action(context.coverage.run_id)}."
        )
    return f"{run_summary}; {reviewed}; {NEXT_MANUAL_OBSERVATION_ACTION}"


__all__ = [
    "add_mvp_readiness_row",
    "mvp_readiness_details",
    "mvp_readiness_status",
    "NEXT_MANUAL_OBSERVATION_ACTION",
]
