from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.review_queue_commands import (
    local_review_caveat,
    outcome_label_guide,
    powershell_double_quoted_text,
    record_outcomes_command,
    record_outcome_command,
    record_outcomes_dry_run_command,
    review_queue_decisions_template_command,
    review_queue_worksheet_command,
    run_outcome_decisions_path,
)
from wraeclast_quant.reports.review_queue_worksheet_sections import (
    manual_review_note_rows,
    opportunity_rows,
    outcome_command_option_rows,
)
from wraeclast_quant.storage.models import StoredOpportunityRecord


def render_review_queue_worksheet(
    run_id: int,
    source_mode: str,
    opportunities: list[StoredOpportunityRecord],
    context_markdown: str | None = None,
    database_path: object | None = None,
) -> str:
    decisions_path = run_outcome_decisions_path(run_id)
    review_coverage_command = f"wq review-coverage --run-id {run_id}"
    if database_path is not None:
        review_coverage_command = (
            f"wq review-coverage --database-path {database_path} --run-id {run_id}"
        )
    rows = [
        "# Wraeclast Quant Review Queue",
        "",
        "Local review worksheet only. No outcome decisions have been recorded.",
        local_review_caveat(source_mode),
        "",
        f"- Run: #{run_id}",
        f"- Source mode: {source_mode}",
        "",
    ]
    if context_markdown:
        rows.extend(
            [
                "## Local Review Context",
                "",
                "Included from a user-supplied local context file. Keep this worksheet local; do not publish it.",
                "",
                context_markdown.strip(),
                "",
            ]
        )
    rows.extend(
        [
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
    )
    rows.extend(opportunity_rows(run_id, opportunities, database_path=database_path))
    rows.extend(
        [
            "",
            "## Review Checklist",
            "",
            "- Inspect each item in your local market context before choosing an outcome.",
            "- Choose exactly one outcome label per item: positive, neutral, or negative.",
            "- Use the batch decisions JSON plus dry-run path, or run only the matching local "
            "`record-outcome` command after you decide.",
            f"- Rerun `{review_coverage_command}` to confirm the reviewed count changed.",
            "",
            "## Batch Outcome Template",
            "",
            "For batch review, write the editable decisions JSON, fill one outcome per item, "
            "dry-run the file, then record it:",
            "",
            f"- Template: `{review_queue_decisions_template_command(run_id, database_path=database_path)}`",
            f"- Dry run: `{record_outcomes_dry_run_command(decisions_path, database_path=database_path)}`",
            f"- Record: `{record_outcomes_command(decisions_path, database_path=database_path)}`",
            "",
            "## Outcome Command Options",
            "",
            *outcome_command_option_rows(
                run_id,
                opportunities,
                database_path=database_path,
            ),
            "",
            "## Manual Review Notes",
            "",
            *manual_review_note_rows(opportunities),
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
    context_markdown: str | None = None,
    database_path: object | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_review_queue_worksheet(
            run_id,
            source_mode,
            opportunities,
            context_markdown=context_markdown,
            database_path=database_path,
        ),
        encoding="utf-8",
    )


__all__ = [
    "local_review_caveat",
    "outcome_label_guide",
    "powershell_double_quoted_text",
    "record_outcomes_command",
    "record_outcomes_dry_run_command",
    "record_outcome_command",
    "review_queue_decisions_template_command",
    "render_review_queue_worksheet",
    "review_queue_worksheet_command",
    "run_outcome_decisions_path",
    "write_review_queue_worksheet",
]
