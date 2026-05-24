from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import format_score, section, table


def opportunities_section(opportunities: list[dict[str, Any]]) -> str:
    return section(
        "Top Opportunities",
        table(
            ["Item", "Score", "Action"],
            [
                [
                    opportunity.get("item_name", ""),
                    format_score(opportunity.get("opportunity_score")),
                    opportunity.get("action", ""),
                ]
                for opportunity in opportunities
            ],
            empty_message="No opportunities found.",
        ),
    )


__all__ = ["opportunities_section"]
