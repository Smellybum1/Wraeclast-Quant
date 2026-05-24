from __future__ import annotations

from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison
from wraeclast_quant.reports.market_brief_formatting import format_delta, format_score


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
        lines.extend(
            [
                "### Top Score Movers",
                "",
                "| Item | Previous | Latest | Delta | Action |",
                "| --- | ---: | ---: | ---: | --- |",
            ]
        )
        for delta in top_movers:
            lines.append(
                f"| {delta.item_name} | {format_score(delta.previous_score)} | "
                f"{format_score(delta.latest_score)} | {format_delta(delta.score_delta)} | "
                f"{delta.latest_action or ''} |"
            )
        lines.append("")

    if status_changes:
        lines.extend(
            [
                "### Action Changes / New / Removed",
                "",
                "| Item | Status | Previous Action | Latest Action | Delta |",
                "| --- | --- | --- | --- | ---: |",
            ]
        )
        for delta in status_changes:
            lines.append(
                f"| {delta.item_name} | {delta.status} | {delta.previous_action or ''} | "
                f"{delta.latest_action or ''} | {format_delta(delta.score_delta)} |"
            )
        lines.append("")

    return lines


__all__ = ["render_snapshot_changes_section"]
