from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.health import DatabaseHealthError, check_database_health
from wraeclast_quant.storage.migration_models import MigrationReadinessCheck
from wraeclast_quant.storage.migration_rows import add_blocker


def add_database_health_check(
    checks: list[MigrationReadinessCheck],
    blockers: list[str],
    database_path: Path,
) -> int | None:
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
        return None

    if health.ok:
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
        return health.latest_run_id

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
    return None


__all__ = ["add_database_health_check"]
