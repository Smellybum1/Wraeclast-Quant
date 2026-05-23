from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.backups import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    list_database_backups,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.health import DatabaseHealthError, check_database_health
from wraeclast_quant.storage.migration_models import (
    MigrationReadinessCheck,
    MigrationReadinessResult,
)
from wraeclast_quant.storage.migration_rows import add_blocker, backup_check_row
from wraeclast_quant.storage.schema import SQLITE_SCHEMA_VERSION


def check_migration_readiness(
    database_path: Path = DEFAULT_DATABASE_PATH,
    backup_dir: Path = DEFAULT_BACKUP_DIR,
) -> MigrationReadinessResult:
    checks: list[MigrationReadinessCheck] = []
    blockers: list[str] = []
    latest_database_run_id: int | None = None
    latest_backup_run_id: int | None = None

    checks.append(
        MigrationReadinessCheck(
            key="schema_version",
            check="SQLite schema version",
            status="ok",
            details=f"v{SQLITE_SCHEMA_VERSION}",
        )
    )

    try:
        health = check_database_health(database_path)
    except DatabaseHealthError as error:
        add_blocker(
            checks,
            blockers,
            "database_health",
            "Database health",
            "invalid",
            str(error),
        )
        health = None

    if health is None:
        add_blocker(
            checks,
            blockers,
            "database_health",
            "Database health",
            "missing",
            f"No database found at {database_path}.",
        )
    elif health.ok:
        latest_database_run_id = health.latest_run_id
        checks.append(
            MigrationReadinessCheck(
                key="database_health",
                check="Database health",
                status="ok",
                details=(
                    f"schema v{health.schema_version}; integrity {health.integrity_message}; "
                    f"{health.analysis_run_count or 0} runs"
                ),
            )
        )
    else:
        add_blocker(
            checks,
            blockers,
            "database_health",
            "Database health",
            "invalid",
            (
                f"schema v{health.schema_version}; integrity {health.integrity_message}; "
                f"missing tables: {', '.join(health.missing_tables) or 'none'}"
            ),
        )

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
    elif not latest_backup.valid:
        add_blocker(
            checks,
            blockers,
            "latest_backup",
            "Latest backup",
            "invalid",
            latest_backup.error,
        )
    else:
        latest_backup_run_id = latest_backup.latest_run_id
        checks.append(backup_check_row(latest_backup))

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

    checks.append(
        MigrationReadinessCheck(
            key="migration_readiness",
            check="Migration readiness",
            status="ready" if not blockers else "not ready",
            details="Ready for schema-change planning." if not blockers else "Resolve blockers before schema changes.",
        )
    )
    return MigrationReadinessResult(
        ready=not blockers,
        schema_version=SQLITE_SCHEMA_VERSION,
        latest_database_run_id=latest_database_run_id,
        latest_backup_run_id=latest_backup_run_id,
        checks=checks,
        blockers=blockers,
    )
