from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.review_queue_commands import batch_outcome_review_next_action
from wraeclast_quant.reports.static_site_html import key_value_table, section


NEXT_MANUAL_OBSERVATION_ACTION = (
    "Run wq currency-exchange-manual-snapshot --input-path <current-snapshot>, "
    "then follow docs/MVP_DAILY_WORKFLOW.md to create <manual-import-output> "
    "and run wq daily --input-path <manual-import-output>"
)


def compliance_section(compliance: dict[str, Any], status_counts: dict[str, Any]) -> str:
    rows = [
        ("Total resources", compliance.get("total_resources", 0)),
        ("Automation eligible", compliance.get("automation_eligible_count", 0)),
    ]
    rows.extend((str(status), count) for status, count in sorted(status_counts.items()))
    return section("Compliance Summary", key_value_table(rows))


def mvp_readiness_section(latest_run: dict[str, Any], coverage: dict[str, Any]) -> str:
    run_id = latest_run.get("id", "")
    if run_id == "":
        rows = [
            ("Local loop", "Needs first run"),
            ("Next action", NEXT_MANUAL_OBSERVATION_ACTION),
        ]
        return section("MVP Readiness", key_value_table(rows))

    total = int(coverage.get("total_recommendations", 0) or 0)
    reviewed = int(coverage.get("reviewed_recommendations", 0) or 0)
    unreviewed = int(coverage.get("unreviewed_recommendations", 0) or 0)
    rows = [
        ("Local loop", "No-OAuth local decision-support ready"),
        ("Latest run", run_id),
        ("Review state", f"{reviewed}/{total} reviewed"),
    ]
    if unreviewed:
        rows.append(("Next action", _review_action_text(run_id)))
    else:
        rows.append(("Next action", NEXT_MANUAL_OBSERVATION_ACTION))
    return section("MVP Readiness", key_value_table(rows))


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
    return f"Run {batch_outcome_review_next_action(str(run_arg))}"


def outcome_summary_section(summary: dict[str, Any]) -> str:
    rows = [(str(outcome), summary.get(outcome, 0)) for outcome in ["positive", "neutral", "negative"]]
    if not summary:
        rows = [("positive", 0), ("neutral", 0), ("negative", 0)]
    return section("Recommendation Outcome Summary", key_value_table(rows))
