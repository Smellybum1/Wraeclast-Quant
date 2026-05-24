from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import format_delta, format_score, section, table


def movers_section(movers: list[dict[str, Any]]) -> str:
    if not movers:
        return section("Snapshot Top Movers", '<p class="empty">No score changes.</p>')
    return section(
        "Snapshot Top Movers",
        table(
            ["Item", "Previous", "Latest", "Delta", "Action"],
            [
                [
                    mover.get("item_name", ""),
                    format_score(mover.get("previous_score")),
                    format_score(mover.get("latest_score")),
                    format_delta(mover.get("score_delta")),
                    mover.get("latest_action", ""),
                ]
                for mover in movers
            ],
        ),
    )


def status_changes_section(changes: list[dict[str, Any]]) -> str:
    if not changes:
        return section(
            "Action Changes / New / Removed",
            '<p class="empty">No action, new, or removed changes.</p>',
        )
    return section(
        "Action Changes / New / Removed",
        table(
            ["Item", "Status", "Previous Action", "Latest Action", "Delta"],
            [
                [
                    change.get("item_name", ""),
                    change.get("status", ""),
                    change.get("previous_action", ""),
                    change.get("latest_action", ""),
                    format_delta(change.get("score_delta")),
                ]
                for change in changes
            ],
        ),
    )


__all__ = ["movers_section", "status_changes_section"]
