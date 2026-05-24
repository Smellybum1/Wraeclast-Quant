from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import (
    badge,
    format_delta,
    format_score,
    section,
    table,
)


def alerts_section(alerts: list[dict[str, Any]]) -> str:
    if not alerts:
        return section("Alert Candidates", '<p class="empty">No alert candidates.</p>')
    return section(
        "Alert Candidates",
        table(
            ["Severity", "Item", "Reason", "Latest", "Delta"],
            [
                [
                    badge(alert.get("severity", "")),
                    alert.get("item_name", ""),
                    alert.get("reason", ""),
                    format_score(alert.get("latest_score")),
                    format_delta(alert.get("score_delta")),
                ]
                for alert in alerts
            ],
        ),
    )


__all__ = ["alerts_section"]
