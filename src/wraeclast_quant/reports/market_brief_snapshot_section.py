from __future__ import annotations

from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison
from wraeclast_quant.reports.market_brief_snapshot_tables import (
    action_changes_section,
    top_score_movers_section,
)


def render_snapshot_changes_section(comparison: SnapshotComparison, limit: int = 5) -> list[str]:
    lines = [
        "## Snapshot Changes",
        "",
        f"Compared run #{comparison.latest_run_id} against run #{comparison.previous_run_id}.",
        "",
    ]
    top_movers = comparison.top_movers[:limit]
    status_changes = comparison.status_changes[:limit]
    if not top_movers and not status_changes:
        lines.extend(["No score, action, new, or removed item changes were detected.", ""])
        return lines

    if top_movers:
        lines.extend(top_score_movers_section(top_movers))

    if status_changes:
        lines.extend(action_changes_section(status_changes))

    return lines


__all__ = ["render_snapshot_changes_section"]
