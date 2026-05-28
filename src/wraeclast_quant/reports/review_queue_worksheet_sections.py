from __future__ import annotations

from wraeclast_quant.reports.outcome_markdown import escape_cell
from wraeclast_quant.reports.review_queue_commands import record_outcome_command
from wraeclast_quant.storage.models import StoredOpportunityRecord


def opportunity_rows(
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
    *,
    database_path: object | None = None,
) -> list[str]:
    rows = []
    for opportunity in opportunities:
        command = record_outcome_command(
            run_id,
            opportunity.item_name,
            outcome="<decision>",
            database_path=database_path,
        )
        rows.append(
            f"| {escape_cell(opportunity.item_name)} | "
            f"{opportunity.opportunity_score:.2f} | "
            f"{escape_cell(opportunity.action)} | "
            "positive / neutral / negative | "
            f"`{escape_cell(command)}` |"
        )
    return rows


def outcome_command_option_rows(
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
    *,
    database_path: object | None = None,
) -> list[str]:
    rows = []
    for index, opportunity in enumerate(opportunities):
        if index:
            rows.append("")
        rows.append(f"### {opportunity.item_name}")
        rows.append("")
        for outcome in ["positive", "neutral", "negative"]:
            command = record_outcome_command(
                run_id,
                opportunity.item_name,
                outcome=outcome,
                database_path=database_path,
            )
            rows.append(f"- `{outcome}`: `{command}`")
    return rows


def manual_review_note_rows(opportunities: list[StoredOpportunityRecord]) -> list[str]:
    rows = []
    for index, opportunity in enumerate(opportunities):
        if index:
            rows.append("")
        rows.append(f"- {opportunity.item_name}:")
        rows.append("  - Decision: positive / neutral / negative")
        rows.append("  - Local notes:")
        rows.append("  - Chosen command:")
    return rows


__all__ = [
    "manual_review_note_rows",
    "opportunity_rows",
    "outcome_command_option_rows",
]
