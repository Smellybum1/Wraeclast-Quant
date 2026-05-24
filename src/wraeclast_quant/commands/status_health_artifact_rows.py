from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_artifact_row_specs import artifact_status_rows
from wraeclast_quant.commands.status_health_artifact_statuses import build_artifact_row_statuses
from wraeclast_quant.commands.status_health_context import StatusHealthContext
from wraeclast_quant.commands.status_health_rows import add_status_row


def add_artifact_rows(
    status_rows: list[dict[str, str]],
    strict_rows: list[tuple[str, str]],
    context: StatusHealthContext,
    *,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    bundle_dir: Path,
) -> None:
    row_statuses = build_artifact_row_statuses(context, intel_path=intel_path)
    strict_rows.extend(row_statuses.strict_rows())
    for row in artifact_status_rows(
        context,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        bundle_dir=bundle_dir,
        row_statuses=row_statuses,
    ):
        add_status_row(status_rows, row.label, row.status, row.details)


__all__ = ["add_artifact_rows"]
