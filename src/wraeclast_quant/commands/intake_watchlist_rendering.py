from __future__ import annotations

from typing import Protocol

from rich.table import Table

from wraeclast_quant.commands.intake_rendering import console
from wraeclast_quant.reports.review_guidance import (
    calibration_prompt_next_action,
    review_next_action,
)
from wraeclast_quant.reports.review_queue_worksheet import (
    local_review_caveat,
)
from wraeclast_quant.storage.models import ReviewCoverageRecord


class WatchlistOpportunity(Protocol):
    item_name: str
    opportunity_score: float
    action: str


def hidden_watchlist_items_text(
    *,
    displayed_count: int,
    total_count: int,
    max_limit: int = 50,
) -> str | None:
    if total_count <= displayed_count:
        return None
    next_limit = min(total_count, max_limit)
    detail = "all" if next_limit == total_count else "more"
    return (
        f"Showing top {displayed_count} of {total_count} scored opportunities. "
        f"Re-run with --limit {next_limit} to show {detail}."
    )


def print_watchlist_table(
    *,
    title: str,
    opportunities: list[WatchlistOpportunity],
    total_count: int | None = None,
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
    if total_count is not None:
        hidden_items = hidden_watchlist_items_text(
            displayed_count=len(opportunities),
            total_count=total_count,
        )
        if hidden_items is not None:
            console.print(hidden_items)


def print_watchlist_review_guidance(
    *,
    run_id: int,
    source_mode: str,
    coverage: ReviewCoverageRecord,
    calibration_prompts: list[str] | None = None,
) -> None:
    console.print(local_review_caveat(source_mode))
    console.print(review_next_action(run_id, coverage))
    if calibration_prompts:
        console.print(calibration_prompt_next_action(len(calibration_prompts)))


__all__ = [
    "calibration_prompt_next_action",
    "hidden_watchlist_items_text",
    "print_watchlist_review_guidance",
    "print_watchlist_table",
    "review_next_action",
]
