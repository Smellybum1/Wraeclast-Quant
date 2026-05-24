from __future__ import annotations

from wraeclast_quant.intelligence.snapshot_deltas import OpportunityDelta
from wraeclast_quant.reports.market_brief_formatting import format_delta, format_score


def top_score_movers_section(top_movers: list[OpportunityDelta]) -> list[str]:
    lines = [
        "### Top Score Movers",
        "",
        "| Item | Previous | Latest | Delta | Action |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for delta in top_movers:
        lines.append(
            f"| {delta.item_name} | {format_score(delta.previous_score)} | "
            f"{format_score(delta.latest_score)} | {format_delta(delta.score_delta)} | "
            f"{delta.latest_action or ''} |"
        )
    lines.append("")
    return lines


def action_changes_section(status_changes: list[OpportunityDelta]) -> list[str]:
    lines = [
        "### Action Changes / New / Removed",
        "",
        "| Item | Status | Previous Action | Latest Action | Delta |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for delta in status_changes:
        lines.append(
            f"| {delta.item_name} | {delta.status} | {delta.previous_action or ''} | "
            f"{delta.latest_action or ''} | {format_delta(delta.score_delta)} |"
        )
    lines.append("")
    return lines


__all__ = ["action_changes_section", "top_score_movers_section"]
