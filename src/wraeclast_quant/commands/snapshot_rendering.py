from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.intelligence.alerts import AlertCandidate
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison

console = Console(width=260)


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
            _format_score(delta.previous_score),
            _format_score(delta.latest_score),
            _format_delta(delta.score_delta),
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
            _format_delta(delta.score_delta),
        )
    console.print(changes_table)


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
            _format_score(candidate.previous_score),
            _format_score(candidate.latest_score),
            _format_delta(candidate.score_delta),
            _format_action_change(candidate),
        )
    console.print(table)


def _format_score(score: float | None) -> str:
    if score is None:
        return ""
    return f"{score:.2f}"


def _format_delta(delta: float | None) -> str:
    if delta is None:
        return ""
    return f"{delta:+.2f}"


def _format_action_change(candidate: AlertCandidate) -> str:
    if candidate.previous_action and candidate.latest_action:
        return f"{candidate.previous_action} -> {candidate.latest_action}"
    return candidate.latest_action or candidate.previous_action or ""
