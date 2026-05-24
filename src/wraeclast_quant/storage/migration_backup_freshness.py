from __future__ import annotations

from wraeclast_quant.storage.migration_models import MigrationReadinessCheck
from wraeclast_quant.storage.migration_rows import add_blocker


def add_backup_freshness_check(
    checks: list[MigrationReadinessCheck],
    blockers: list[str],
    *,
    latest_database_run_id: int | None,
    latest_backup_run_id: int | None,
) -> None:
    if latest_database_run_id is None or latest_backup_run_id is None:
        add_blocker(
            checks,
            blockers,
            "backup_freshness",
            "Backup freshness",
            "unknown",
            "Could not compare latest database run to latest backup run.",
        )
    elif latest_backup_run_id != latest_database_run_id:
        add_blocker(
            checks,
            blockers,
            "backup_freshness",
            "Backup freshness",
            "stale",
            (
                f"stale; latest database run #{latest_database_run_id}, "
                f"latest backup run #{latest_backup_run_id}"
            ),
        )
    else:
        checks.append(
            MigrationReadinessCheck(
                key="backup_freshness",
                check="Backup freshness",
                status="ok",
                details=(
                    f"latest database run #{latest_database_run_id}; "
                    f"latest backup run #{latest_backup_run_id}"
                ),
            )
        )


__all__ = ["add_backup_freshness_check"]
