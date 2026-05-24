from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.backups import DatabaseBackupError, list_database_backups
from wraeclast_quant.storage.migration_models import MigrationReadinessCheck
from wraeclast_quant.storage.migration_rows import add_blocker, backup_check_row


def add_latest_backup_check(
    checks: list[MigrationReadinessCheck],
    blockers: list[str],
    backup_dir: Path,
) -> int | None:
    try:
        backups = list_database_backups(backup_dir=backup_dir, limit=1)
    except DatabaseBackupError as error:
        add_blocker(
            checks,
            blockers,
            "latest_backup",
            "Latest backup",
            "invalid",
            str(error),
        )
        backups = []

    latest_backup = backups[0] if backups else None
    if latest_backup is None:
        add_blocker(
            checks,
            blockers,
            "latest_backup",
            "Latest backup",
            "missing",
            f"No local SQLite backups found in {backup_dir}.",
        )
        return None
    if not latest_backup.valid:
        add_blocker(
            checks,
            blockers,
            "latest_backup",
            "Latest backup",
            "invalid",
            latest_backup.error,
        )
        return None

    checks.append(backup_check_row(latest_backup))
    return latest_backup.latest_run_id


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
