from __future__ import annotations

from wraeclast_quant.reports.publish_handoff_formatting import markdown_cell, markdown_value
from wraeclast_quant.reports.publish_models import PublishCheckResult


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


__all__ = ["blocker_lines", "readiness_check_lines"]
