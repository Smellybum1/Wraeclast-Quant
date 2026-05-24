from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_rows import add_blocking_check
from wraeclast_quant.storage.repositories import SnapshotRepository


def add_latest_database_run_check(
    checks: list[PublishCheckRow],
    blockers: list[str],
    database_path: Path,
) -> int | None:
    latest_run = SnapshotRepository(database_path).latest_run()
    latest_database_run_id = latest_run.id if latest_run is not None else None

    if latest_database_run_id is None:
        add_blocking_check(
            checks,
            blockers,
            "database_latest_run",
            "Latest database run",
            "missing",
            "No latest database run found.",
        )
        return None

    checks.append(
        PublishCheckRow(
            key="database_latest_run",
            check="Latest database run",
            status="ok",
            details=f"Run #{latest_database_run_id}",
        )
    )
    return latest_database_run_id


__all__ = ["add_latest_database_run_check"]
