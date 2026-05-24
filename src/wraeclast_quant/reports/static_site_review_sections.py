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
    rows = [
        ("Run", coverage.get("run_id", "")),
        ("Total recommendations", coverage.get("total_recommendations", 0)),
        ("Reviewed", coverage.get("reviewed_recommendations", 0)),
        ("Unreviewed", coverage.get("unreviewed_recommendations", 0)),
        ("Reviewed %", f"{float(coverage.get('reviewed_percent', 0.0)):.1f}%"),
    ]
    return section("Recommendation Review Coverage", key_value_table(rows))


def outcome_summary_section(summary: dict[str, Any]) -> str:
    rows = [(str(outcome), summary.get(outcome, 0)) for outcome in ["positive", "neutral", "negative"]]
    if not summary:
        rows = [("positive", 0), ("neutral", 0), ("negative", 0)]
    return section("Recommendation Outcome Summary", key_value_table(rows))
