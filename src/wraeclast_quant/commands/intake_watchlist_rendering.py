from __future__ import annotations

from typing import Protocol

from rich.table import Table

from wraeclast_quant.commands.intake_rendering import console
from wraeclast_quant.reports.review_queue_worksheet import (
    local_review_caveat,
    review_queue_worksheet_command,
)
from wraeclast_quant.storage.models import ReviewCoverageRecord


class WatchlistOpportunity(Protocol):
    item_name: str
    opportunity_score: float
    action: str


def print_watchlist_table(
    *,
    title: str,
    opportunities: list[WatchlistOpportunity],
) -> None:
    console.print(title)
    table = Table(title="Watchlist")
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


def print_watchlist_review_guidance(
    *,
    run_id: int,
    source_mode: str,
    coverage: ReviewCoverageRecord,
) -> None:
    console.print(local_review_caveat(source_mode))
    console.print(review_next_action(run_id, coverage))


def review_next_action(run_id: int, coverage: ReviewCoverageRecord) -> str:
    reviewed = f"{coverage.reviewed_recommendations}/{coverage.total_recommendations} reviewed"
    if coverage.unreviewed_recommendations:
        return (
            f"Review coverage: {reviewed}; {coverage.unreviewed_recommendations} unreviewed. "
            f"Next: {review_queue_worksheet_command(run_id)}."
        )
    return f"Review coverage: {reviewed}; all recommendations for run #{run_id} have outcomes."


__all__ = [
    "print_watchlist_review_guidance",
    "print_watchlist_table",
    "review_next_action",
]
