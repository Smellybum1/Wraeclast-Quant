from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.static_site_sections import (
    alerts_section,
    compliance_section,
    mvp_readiness_section,
    movers_section,
    opportunities_section,
    outcome_summary_section,
    recent_runs_section,
    review_coverage_section,
    score_trends_section,
    status_changes_section,
    summary_section,
)


def dashboard_sections(
    payload: dict[str, Any],
    latest_run: dict[str, Any],
    compliance: dict[str, Any],
    status_counts: dict[str, Any],
    changes: dict[str, Any],
) -> list[str]:
    return [
        summary_section(payload, latest_run),
        mvp_readiness_section(latest_run, payload.get("review_coverage") or {}),
        recent_runs_section(payload.get("recent_runs") or []),
        score_trends_section(payload.get("score_trends") or []),
        review_coverage_section(payload.get("review_coverage") or {}),
        outcome_summary_section(payload.get("outcome_summary") or {}),
        compliance_section(compliance, status_counts),
        alerts_section(payload.get("alerts") or []),
        opportunities_section(payload.get("top_opportunities") or []),
        movers_section(changes.get("top_movers") or []),
        status_changes_section(changes.get("status_changes") or []),
    ]


__all__ = ["dashboard_sections"]
