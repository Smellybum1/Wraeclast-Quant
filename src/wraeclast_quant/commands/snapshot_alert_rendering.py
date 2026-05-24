from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands.snapshot_console import console
from wraeclast_quant.commands.snapshot_formatting import (
    format_action_change,
    format_delta,
    format_score,
)
from wraeclast_quant.intelligence.alerts import AlertCandidate


def print_alert_candidates(candidates: list[AlertCandidate], limit: int) -> None:
    if not candidates:
        console.print("No alert candidates found.")
        return

    table = Table(title="Local Alert Preview")
    table.add_column("Severity")
    table.add_column("Item")
    table.add_column("Reason")
    table.add_column("Previous", justify="right")
    table.add_column("Latest", justify="right")
    table.add_column("Delta", justify="right")
    table.add_column("Action")
    for candidate in candidates[:limit]:
        table.add_row(
            candidate.severity,
            candidate.item_name,
            candidate.reason,
            format_score(candidate.previous_score),
            format_score(candidate.latest_score),
            format_delta(candidate.score_delta),
            format_action_change(candidate),
        )
    console.print(table)


__all__ = ["print_alert_candidates"]
