from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_artifact_rows import add_artifact_rows
from wraeclast_quant.commands.status_health_calibration_rows import add_calibration_prompt_row
from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_latest_rows import add_latest_run_rows
from wraeclast_quant.commands.status_health_models import StatusHealthReport
from wraeclast_quant.commands.status_health_mvp_rows import add_mvp_readiness_row
from wraeclast_quant.commands.status_health_overview_rows import add_overview_rows
from wraeclast_quant.commands.status_health_rows import strict_failure_keys
from wraeclast_quant.commands.status_health_safety_rows import add_backup_and_safety_rows


def build_status_report_from_context(
    context: StatusHealthContext,
    *,
    database_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
    stash_ninja_path: Path,
) -> StatusHealthReport:
    status_rows: list[dict[str, str]] = []
    strict_rows: list[tuple[str, str]] = []
    add_overview_rows(status_rows, strict_rows, context, database_path=database_path)
    add_latest_run_rows(status_rows, context)
    add_mvp_readiness_row(status_rows, context)
    add_calibration_prompt_row(status_rows, context)
    add_artifact_rows(
        status_rows,
        strict_rows,
        context,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
        stash_ninja_path=stash_ninja_path,
    )
    add_backup_and_safety_rows(status_rows, strict_rows, context)
    strict_failures = [label for label, row_status in strict_rows if row_status == "needs attention"]
    return StatusHealthReport(
        rows=status_rows,
        strict_failures=strict_failures,
        strict_failure_keys=strict_failure_keys(strict_failures),
    )
