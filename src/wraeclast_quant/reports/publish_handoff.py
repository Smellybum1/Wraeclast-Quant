from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from wraeclast_quant.reports.publish_models import PublishCheckResult

DEFAULT_PUBLISH_HANDOFF_PATH = Path("data/processed/publish_handoff.md")


def render_publish_handoff(result: PublishCheckResult) -> str:
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    readiness = "ready" if result.ready else "not ready"
    files = result.files if result.files else ["None"]
    blockers = result.blockers if result.blockers else ["None"]

    lines = [
        "# Wraeclast Quant Manual Publish Handoff",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Manual publishing readiness: `{readiness}`",
        f"- Latest database run: `{_run_label(result.latest_database_run_id)}`",
        f"- Bundle latest run: `{_run_label(result.bundle_latest_run_id)}`",
        f"- Archive path: `{result.archive_path}`",
        "",
        "## Bundle Files",
        "",
    ]
    lines.extend(f"- `{file_name}`" for file_name in files)
    lines.extend(
        [
            "",
            "## Readiness Checks",
            "",
            "| Check | Status | Details |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(
        f"| {_markdown_cell(row.check)} | {_markdown_cell(row.status)} | {_markdown_cell(row.details)} |"
        for row in result.checks
    )
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {_markdown_value(blocker)}" for blocker in blockers)
    lines.extend(
        [
            "",
            "## Manual Publishing Checklist",
            "",
            "- [ ] Confirm `wq publish-check` reports ready.",
            "- [ ] Inspect the static dashboard locally.",
            "- [ ] Inspect `public_intel.json` for derived-only content.",
            "- [ ] Confirm the bundle archive contains only the expected static files.",
            "- [ ] Manually publish outside Wraeclast Quant only if you choose to.",
            "",
            "## Safety Boundary",
            "",
            "This handoff is local-only and derived-only. Wraeclast Quant did not upload, host, publish, start a server, make network calls, call webhooks, post to Discord, scrape sources, approve sources, automate gameplay, perform trades, send whispers, click UI, move characters, or interact with the game client.",
            "",
            "Do not include unprocessed signal payloads, source data excerpts, resource notes, credentials, cookies, tokens, or secret environment values in a public handoff.",
            "",
        ]
    )
    return "\n".join(lines)


def write_publish_handoff(
    result: PublishCheckResult,
    output_path: str | Path = DEFAULT_PUBLISH_HANDOFF_PATH,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_publish_handoff(result), encoding="utf-8")
    return path


def _run_label(run_id: int | None) -> str:
    return f"#{run_id}" if run_id is not None else "none"


def _markdown_cell(value: str) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def _markdown_value(value: str) -> str:
    normalized = " ".join(str(value).split())
    return normalized or "None"
