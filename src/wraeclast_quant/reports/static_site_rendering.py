from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_html import metadata_tags
from wraeclast_quant.reports.static_site_sections import (
    alerts_section,
    compliance_section,
    movers_section,
    opportunities_section,
    outcome_summary_section,
    recent_runs_section,
    review_coverage_section,
    score_trends_section,
    status_changes_section,
    summary_section,
)
from wraeclast_quant.reports.static_site_styles import static_site_css


def render_static_site(payload: dict[str, Any]) -> str:
    latest_run = payload.get("latest_run") or {}
    compliance = payload.get("compliance_summary") or {}
    status_counts = compliance.get("status_counts") or {}
    changes = payload.get("snapshot_changes") or {}

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            *metadata_tags(payload, latest_run),
            "  <title>Wraeclast Quant</title>",
            f"  <style>{static_site_css()}</style>",
            "</head>",
            "<body>",
            '  <main class="shell">',
            "    <header>",
            "      <h1>Wraeclast Quant</h1>",
            "      <p>Local market intelligence preview. Research output only.</p>",
            "    </header>",
            summary_section(payload, latest_run),
            recent_runs_section(payload.get("recent_runs") or []),
            score_trends_section(payload.get("score_trends") or []),
            review_coverage_section(payload.get("review_coverage") or {}),
            outcome_summary_section(payload.get("outcome_summary") or {}),
            compliance_section(compliance, status_counts),
            alerts_section(payload.get("alerts") or []),
            opportunities_section(payload.get("top_opportunities") or []),
            movers_section(changes.get("top_movers") or []),
            status_changes_section(changes.get("status_changes") or []),
            "  </main>",
            "</body>",
            "</html>",
            "",
        ]
    )
