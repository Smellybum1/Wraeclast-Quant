from __future__ import annotations

from wraeclast_quant.storage.backups import DatabaseBackupListing
from wraeclast_quant.storage.migration_models import MigrationReadinessCheck


def backup_check_row(backup: DatabaseBackupListing) -> MigrationReadinessCheck:
    return MigrationReadinessCheck(
        key="latest_backup",
        check="Latest backup",
        status="ok",
        details=(
            f"{backup.backup_path}; latest run #{backup.latest_run_id or 'none'}; "
            f"{backup.analysis_run_count or 0} runs"
        ),
    )


def add_blocker(
    checks: list[MigrationReadinessCheck],
    blockers: list[str],
    key: str,
    check: str,
    status: str,
    details: str,
) -> None:
    checks.append(
        MigrationReadinessCheck(
            key=key,
            check=check,
            status=status,
            details=details,
        )
    )
    blockers.append(f"{check}: {details}")
