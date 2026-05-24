from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_artifact_rows import add_artifact_rows
from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_latest_rows import add_latest_run_rows
from wraeclast_quant.commands.status_health_models import StatusHealthReport
from wraeclast_quant.commands.status_health_rows import add_status_row, strict_failure_keys
from wraeclast_quant.commands.status_health_safety_rows import add_backup_and_safety_rows
from wraeclast_quant.commands.status_health_storage import (
    database_health_details,
    database_health_status,
    exists_label,
)


def build_status_report_from_context(
    context: StatusHealthContext,
    *,
    database_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
) -> StatusHealthReport:
    status_rows: list[dict[str, str]] = []
    strict_rows: list[tuple[str, str]] = []
    add_status_row(
        status_rows,
        "Resources",
        "ok",
        f"{len(context.resources)} configured; {context.eligible_count} automation-eligible",
    )
    add_status_row(status_rows, "Database", exists_label(context.database_exists), str(database_path))

    database_health_row_status = database_health_status(context.database_health)
    strict_rows.append(("Database health", database_health_row_status))
    add_status_row(
        status_rows,
        "Database health",
        database_health_row_status,
        database_health_details(context.database_health),
    )
    add_latest_run_rows(status_rows, context)
    add_artifact_rows(
        status_rows,
        strict_rows,
        context,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
    )
    add_backup_and_safety_rows(status_rows, strict_rows, context)
    strict_failures = [label for label, row_status in strict_rows if row_status == "needs attention"]
    return StatusHealthReport(
        rows=status_rows,
        strict_failures=strict_failures,
        strict_failure_keys=strict_failure_keys(strict_failures),
    )
