from __future__ import annotations

from wraeclast_quant.reports.publish_handoff_formatting import run_label
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


__all__ = ["bundle_file_lines", "summary_lines"]
