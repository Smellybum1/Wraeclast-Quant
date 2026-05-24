from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import (
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
