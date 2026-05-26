from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import key_value_table, section


def compliance_section(compliance: dict[str, Any], status_counts: dict[str, Any]) -> str:
    rows = [
        ("Total resources", compliance.get("total_resources", 0)),
        ("Automation eligible", compliance.get("automation_eligible_count", 0)),
    ]
    rows.extend((str(status), count) for status, count in sorted(status_counts.items()))
    return section("Compliance Summary", key_value_table(rows))


def review_coverage_section(coverage: dict[str, Any]) -> str:
    run_id = coverage.get("run_id", "")
    unreviewed = int(coverage.get("unreviewed_recommendations", 0) or 0)
    rows = [
        ("Run", run_id),
        ("Total recommendations", coverage.get("total_recommendations", 0)),
        ("Reviewed", coverage.get("reviewed_recommendations", 0)),
        ("Unreviewed", unreviewed),
        ("Reviewed %", f"{float(coverage.get('reviewed_percent', 0.0)):.1f}%"),
    ]
    if unreviewed:
        rows.append(("Next review action", _review_action_text(run_id)))
    return section("Recommendation Review Coverage", key_value_table(rows))


def _review_action_text(run_id: object) -> str:
    run_arg = run_id if run_id != "" else "<id>"
    return (
        "Run wq review-queue, then "
        f"wq record-outcome --run-id {run_arg} --item-name <name> "
        "--outcome positive|neutral|negative"
    )


def outcome_summary_section(summary: dict[str, Any]) -> str:
    rows = [(str(outcome), summary.get(outcome, 0)) for outcome in ["positive", "neutral", "negative"]]
    if not summary:
        rows = [("positive", 0), ("neutral", 0), ("negative", 0)]
    return section("Recommendation Outcome Summary", key_value_table(rows))
