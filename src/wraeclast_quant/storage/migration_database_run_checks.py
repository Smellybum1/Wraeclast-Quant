from __future__ import annotations

from wraeclast_quant.storage.migration_models import MigrationReadinessCheck
from wraeclast_quant.storage.migration_rows import add_blocker


def add_latest_database_run_check(
    checks: list[MigrationReadinessCheck],
    blockers: list[str],
    latest_database_run_id: int | None,
) -> None:
    if latest_database_run_id is None:
        add_blocker(
            checks,
            blockers,
            "latest_database_run",
            "Latest database run",
            "missing",
            "No latest analysis run found.",
        )
    else:
        checks.append(
            MigrationReadinessCheck(
                key="latest_database_run",
                check="Latest database run",
                status="ok",
                details=f"Run #{latest_database_run_id}",
            )
        )


__all__ = ["add_latest_database_run_check"]
