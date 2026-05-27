from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.outcome_markdown import escape_cell
from wraeclast_quant.storage.models import StoredOpportunityRecord


def local_review_caveat(source_mode: str) -> str:
    return (
        f"Run source: {source_mode}. Review outcomes are local decision-support only; "
        "no trades, whispers, gameplay, publishing, or live collection are performed."
    )


def outcome_label_guide() -> str:
    return (
        "Outcome labels: positive=useful signal, neutral=mixed or unclear, "
        "negative=not useful after review."
    )


def review_queue_worksheet_command(run_id: int) -> str:
    return (
        f"wq review-queue --run-id {run_id} "
        "--output-path data/processed/review_queue.md"
    )


def record_outcome_command(
    run_id: int,
    item_name: str,
    *,
    outcome: str = "positive|neutral|negative",
) -> str:
    return (
        "wq record-outcome "
        f"--run-id {run_id} "
        f'--item-name "{powershell_double_quoted_text(item_name)}" '
        f"--outcome {outcome}"
    )


def render_review_queue_worksheet(
    run_id: int,
    source_mode: str,
    opportunities: list[StoredOpportunityRecord],
) -> str:
    rows = [
        "# Wraeclast Quant Review Queue",
        "",
        "Local review worksheet only. No outcome decisions have been recorded.",
        local_review_caveat(source_mode),
        "",
        f"- Run: #{run_id}",
        f"- Source mode: {source_mode}",
        "",
        "## Outcome Labels",
        "",
        "- `positive`: useful signal after manual review.",
        "- `neutral`: mixed, stale, or unclear after manual review.",
        "- `negative`: not useful after manual review.",
        "",
        "## Unreviewed Recommendations",
        "",
        "| Item | Score | Action | Outcome decision | Command |",
        "| --- | ---: | --- | --- | --- |",
    ]
    rows.extend(_opportunity_rows(run_id, opportunities))
    rows.extend(
        [
            "",
            "## Outcome Command Options",
            "",
            *_outcome_command_option_rows(run_id, opportunities),
            "",
            "## Manual Review Notes",
            "",
            *_manual_review_note_rows(opportunities),
            "",
            "Choose one outcome decision per item, then run the matching command locally.",
            "Optional notes stay local; append --notes \"<local note>\" to the chosen command if useful.",
            "Do not record outcomes until a human review decision has been made.",
            "",
        ]
    )
    return "\n".join(rows)


def write_review_queue_worksheet(
    path: Path,
    *,
    run_id: int,
    source_mode: str,
    opportunities: list[StoredOpportunityRecord],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_review_queue_worksheet(run_id, source_mode, opportunities),
        encoding="utf-8",
    )


def powershell_double_quoted_text(value: str) -> str:
    return value.replace("`", "``").replace('"', '`"')


def _opportunity_rows(run_id: int, opportunities: list[StoredOpportunityRecord]) -> list[str]:
    rows = []
    for opportunity in opportunities:
        command = record_outcome_command(run_id, opportunity.item_name, outcome="<decision>")
        rows.append(
            f"| {escape_cell(opportunity.item_name)} | "
            f"{opportunity.opportunity_score:.2f} | "
            f"{escape_cell(opportunity.action)} | "
            "positive / neutral / negative | "
            f"`{escape_cell(command)}` |"
        )
    return rows


def _outcome_command_option_rows(
    run_id: int,
    opportunities: list[StoredOpportunityRecord],
) -> list[str]:
    rows = []
    for index, opportunity in enumerate(opportunities):
        if index:
            rows.append("")
        rows.append(f"### {opportunity.item_name}")
        rows.append("")
        for outcome in ["positive", "neutral", "negative"]:
            command = record_outcome_command(run_id, opportunity.item_name, outcome=outcome)
            rows.append(f"- `{outcome}`: `{command}`")
    return rows


def _manual_review_note_rows(opportunities: list[StoredOpportunityRecord]) -> list[str]:
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
    "local_review_caveat",
    "outcome_label_guide",
    "powershell_double_quoted_text",
    "record_outcome_command",
    "render_review_queue_worksheet",
    "review_queue_worksheet_command",
    "write_review_queue_worksheet",
]
