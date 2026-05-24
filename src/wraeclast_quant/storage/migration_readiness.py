from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.migration_backup_checks import (
    add_backup_freshness_check,
    add_latest_backup_check,
)
from wraeclast_quant.storage.migration_database_checks import add_database_checks
from wraeclast_quant.storage.migration_models import (
    MigrationReadinessCheck,
    MigrationReadinessResult,
)
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

    latest_database_run_id = add_database_checks(checks, blockers, database_path)
    latest_backup_run_id = add_latest_backup_check(checks, blockers, backup_dir)
    add_backup_freshness_check(
        checks,
        blockers,
        latest_database_run_id=latest_database_run_id,
        latest_backup_run_id=latest_backup_run_id,
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
