from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.migration_database_health_checks import add_database_health_check
from wraeclast_quant.storage.migration_database_run_checks import add_latest_database_run_check
from wraeclast_quant.storage.migration_models import MigrationReadinessCheck


def add_database_checks(
    checks: list[MigrationReadinessCheck],
    blockers: list[str],
    database_path: Path,
) -> int | None:
    latest_database_run_id = add_database_health_check(checks, blockers, database_path)
    add_latest_database_run_check(checks, blockers, latest_database_run_id)
    return latest_database_run_id


__all__ = ["add_database_checks"]
