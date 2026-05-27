from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.review_queue_commands import batch_outcome_review_next_action


def render_stash_ninja_watchlist_markdown(payload: dict[str, Any]) -> str:
    run = payload["latest_run"]
    coverage = payload["review_coverage"]
    lines = [
        "# Exile-UI Stash-Ninja Companion Watchlist",
        "",
        "Derived-only local handoff for manually configuring or checking Stash-Ninja. "
        "This file does not write Exile-UI settings, automate the overlay, or interact with the game client.",
        "",
        f"- Run: #{run['id']} ({run['source_mode']})",
        f"- Created at: {run['created_at']}",
        (
            "- Review coverage: "
            f"{coverage['reviewed_recommendations']}/{coverage['total_recommendations']} reviewed "
            f"({coverage['reviewed_percent']:.1f}%)"
        ),
        (
            "- Next manual review: "
            f"{batch_outcome_review_next_action(int(run['id']))}"
        ),
        "",
        "| Item | Score | Action | Suggested manual treatment |",
        "| --- | ---: | --- | --- |",
    ]
    for item in payload["items"]:
        lines.append(
            "| "
            f"{item['item_name']} | "
            f"{item['opportunity_score']:.2f} | "
            f"{item['action']} | "
            f"{item['suggested_stash_ninja_treatment']} |"
        )
    if not payload["items"]:
        lines.append("| _No items met the score threshold._ |  |  |  |")
    lines.extend(
        [
            "",
            "Manual application required: inspect these recommendations yourself before changing any overlay settings.",
            "",
        ]
    )
    return "\n".join(lines)


__all__ = ["render_stash_ninja_watchlist_markdown"]
