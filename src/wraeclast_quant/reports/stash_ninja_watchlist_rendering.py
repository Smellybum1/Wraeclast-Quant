from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.review_guidance import manual_review_handoff_next_action


def render_stash_ninja_watchlist_markdown(payload: dict[str, Any]) -> str:
    run = payload["latest_run"]
    coverage = payload["review_coverage"]
    run_id = int(run["id"])
    next_action = manual_review_handoff_next_action(
        run_id=run_id,
        unreviewed_recommendations=int(coverage["unreviewed_recommendations"]),
        calibration_prompt_count=int(payload.get("calibration_prompt_count", 0)),
    )
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
        _markdown_next_action_line(next_action),
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


def _markdown_next_action_line(next_action: str) -> str:
    if next_action.startswith("Next: "):
        return f"- Next manual review: {next_action.removeprefix('Next: ')}"
    return f"- {next_action}"


__all__ = ["render_stash_ninja_watchlist_markdown"]
