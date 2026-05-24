from __future__ import annotations

from wraeclast_quant.intelligence.scoring import ScoredOpportunity


def render_opportunities_section(opportunities: list[ScoredOpportunity]) -> list[str]:
    lines = [
        "# Wraeclast Quant Market Brief",
        "",
        "Research output only. The user must manually review and execute any trades.",
        "",
        "| Rank | Item | Score | Action |",
        "| --- | --- | ---: | --- |",
    ]
    for index, opportunity in enumerate(opportunities, start=1):
        lines.append(
            f"| {index} | {opportunity.item_name} | "
            f"{opportunity.opportunity_score:.2f} | {opportunity.action} |"
        )
    lines.append("")
    return lines


__all__ = ["render_opportunities_section"]
