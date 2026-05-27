from __future__ import annotations

from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row


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
        return (
            "No local run yet; next: validate a manual import, then run "
            "wq daily --input-path <file>."
        )

    run_summary = f"No-OAuth local loop ready on run #{context.latest.id}"
    if context.coverage is None:
        return f"{run_summary}; next: wq review-queue."

    reviewed = (
        f"{context.coverage.reviewed_recommendations}/"
        f"{context.coverage.total_recommendations} reviewed"
    )
    if context.coverage.unreviewed_recommendations:
        return (
            f"{run_summary}; {reviewed}; next: wq review-queue "
            f"--run-id {context.coverage.run_id} --output-path data/processed/review_queue.md; "
            f"wq record-outcome --run-id {context.coverage.run_id} --item-name <name> "
            "--outcome positive|neutral|negative."
        )
    return (
        f"{run_summary}; {reviewed}; next: prepare the next local manual snapshot "
        "or run wq daily --input-path <file>."
    )


__all__ = [
    "add_mvp_readiness_row",
    "mvp_readiness_details",
    "mvp_readiness_status",
]
