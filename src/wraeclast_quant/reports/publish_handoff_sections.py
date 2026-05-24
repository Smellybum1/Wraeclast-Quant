from __future__ import annotations

from wraeclast_quant.reports.publish_handoff_formatting import (
    markdown_cell,
    markdown_value,
    run_label,
)
from wraeclast_quant.reports.publish_models import PublishCheckResult


def summary_lines(result: PublishCheckResult, generated_at: str) -> list[str]:
    readiness = "ready" if result.ready else "not ready"
    return [
        "# Wraeclast Quant Manual Publish Handoff",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Manual publishing readiness: `{readiness}`",
        f"- Latest database run: `{run_label(result.latest_database_run_id)}`",
        f"- Bundle latest run: `{run_label(result.bundle_latest_run_id)}`",
        f"- Archive path: `{result.archive_path}`",
        "",
        "## Bundle Files",
        "",
    ]


def bundle_file_lines(files: list[str]) -> list[str]:
    file_names = files if files else ["None"]
    return [f"- `{file_name}`" for file_name in file_names]


def readiness_check_lines(result: PublishCheckResult) -> list[str]:
    lines = [
        "",
        "## Readiness Checks",
        "",
        "| Check | Status | Details |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| {markdown_cell(row.check)} | {markdown_cell(row.status)} | {markdown_cell(row.details)} |"
        for row in result.checks
    )
    return lines


def blocker_lines(blockers: list[str]) -> list[str]:
    blocker_values = blockers if blockers else ["None"]
    lines = ["", "## Blockers", ""]
    lines.extend(f"- {markdown_value(blocker)}" for blocker in blocker_values)
    return lines


def manual_checklist_lines() -> list[str]:
    return [
        "",
        "## Manual Publishing Checklist",
        "",
        "- [ ] Confirm `wq publish-check` reports ready.",
        "- [ ] Inspect the static dashboard locally.",
        "- [ ] Inspect `public_intel.json` for derived-only content.",
        "- [ ] Confirm the bundle archive contains only the expected static files.",
        "- [ ] Manually publish outside Wraeclast Quant only if you choose to.",
        "",
    ]


def safety_boundary_lines() -> list[str]:
    return [
        "## Safety Boundary",
        "",
        "This handoff is local-only and derived-only. Wraeclast Quant did not upload, host, publish, start a server, make network calls, call webhooks, post to Discord, scrape sources, approve sources, automate gameplay, perform trades, send whispers, click UI, move characters, or interact with the game client.",
        "",
        "Do not include unprocessed signal payloads, source data excerpts, resource notes, credentials, cookies, tokens, or secret environment values in a public handoff.",
        "",
    ]


__all__ = [
    "blocker_lines",
    "bundle_file_lines",
    "manual_checklist_lines",
    "readiness_check_lines",
    "safety_boundary_lines",
    "summary_lines",
]
