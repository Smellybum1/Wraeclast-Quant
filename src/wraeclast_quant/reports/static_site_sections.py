from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import (
    badge,
    format_delta,
    format_score,
    format_trend_points,
    key_value_table,
    section,
    table,
)


def summary_section(payload: dict[str, Any], latest_run: dict[str, Any]) -> str:
    rows = [
        ("Schema version", payload.get("schema_version", "")),
        ("Generated", payload.get("generated_at", "")),
        ("Latest run", latest_run.get("id", "")),
        ("Source mode", latest_run.get("source_mode", "")),
        ("Item count", latest_run.get("item_count", "")),
    ]
    return section("Run Summary", key_value_table(rows))


def compliance_section(compliance: dict[str, Any], status_counts: dict[str, Any]) -> str:
    rows = [
        ("Total resources", compliance.get("total_resources", 0)),
        ("Automation eligible", compliance.get("automation_eligible_count", 0)),
    ]
    rows.extend((str(status), count) for status, count in sorted(status_counts.items()))
    return section("Compliance Summary", key_value_table(rows))


def recent_runs_section(runs: list[dict[str, Any]]) -> str:
    return section(
        "Recent Runs",
        table(
            ["Run", "Created", "Source", "Items"],
            [
                [
                    run.get("id", ""),
                    run.get("created_at", ""),
                    run.get("source_mode", ""),
                    run.get("item_count", ""),
                ]
                for run in runs
            ],
            empty_message="No recent runs.",
        ),
    )


def score_trends_section(trends: list[dict[str, Any]]) -> str:
    return section(
        "Score Trends",
        table(
            ["Item", "Recent Scores"],
            [
                [
                    trend.get("item_name", ""),
                    format_trend_points(trend.get("points") or []),
                ]
                for trend in trends
            ],
            empty_message="No score trends.",
        ),
    )


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
