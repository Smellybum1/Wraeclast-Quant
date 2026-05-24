from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.storage.backups import DatabaseBackupListing, list_database_backups
from wraeclast_quant.storage.health import DatabaseHealthResult, check_database_health


@dataclass(frozen=True)
class DatabaseStatusContext:
    backups: list[DatabaseBackupListing]
    database_health: DatabaseHealthResult | None
    database_exists: bool


def load_database_status_context(
    *,
    database_path: Path,
    backup_dir: Path,
) -> DatabaseStatusContext:
    return DatabaseStatusContext(
        backups=list_database_backups(backup_dir=backup_dir, limit=1),
        database_health=check_database_health(database_path),
        database_exists=database_path.exists(),
    )


__all__ = ["DatabaseStatusContext", "load_database_status_context"]
