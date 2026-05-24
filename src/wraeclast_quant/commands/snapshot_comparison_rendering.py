from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands.snapshot_console import console
from wraeclast_quant.commands.snapshot_formatting import format_delta, format_score
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison


def print_comparison(comparison: SnapshotComparison, limit: int) -> None:
    console.print(
        f"Comparing run #{comparison.latest_run_id} against run #{comparison.previous_run_id}"
    )

    movers_table = Table(title="Top Movers")
    movers_table.add_column("Item")
    movers_table.add_column("Previous", justify="right")
    movers_table.add_column("Latest", justify="right")
    movers_table.add_column("Delta", justify="right")
    movers_table.add_column("Action")
    top_movers = comparison.top_movers[:limit]
    if not top_movers:
        movers_table.add_row("No score changes found.", "", "", "", "")
    for delta in top_movers:
        movers_table.add_row(
            delta.item_name,
            format_score(delta.previous_score),
            format_score(delta.latest_score),
            format_delta(delta.score_delta),
            delta.latest_action or "",
        )
    console.print(movers_table)

    changes_table = Table(title="Action Changes / New / Removed")
    changes_table.add_column("Item")
    changes_table.add_column("Status")
    changes_table.add_column("Previous Action")
    changes_table.add_column("Latest Action")
    changes_table.add_column("Delta", justify="right")
    status_changes = comparison.status_changes[:limit]
    if not status_changes:
        changes_table.add_row("No action, new, or removed changes found.", "", "", "", "")
    for delta in status_changes:
        changes_table.add_row(
            delta.item_name,
            delta.status,
            delta.previous_action or "",
            delta.latest_action or "",
            format_delta(delta.score_delta),
        )
    console.print(changes_table)


__all__ = ["print_comparison"]
