from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from wraeclast_quant.storage.backup_models import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    DatabaseBackupResult,
)


def backup_database(
    database_path: Path,
    output_dir: Path = DEFAULT_BACKUP_DIR,
    created_at: str | None = None,
) -> DatabaseBackupResult | None:
    if not database_path.exists():
        return None
    if not database_path.is_file():
        raise DatabaseBackupError(f"Database path is not a file: {database_path}")

    timestamp = created_at or datetime.now(UTC).isoformat(timespec="seconds")
    output_dir.mkdir(parents=True, exist_ok=True)
    backup_path = output_dir / f"{database_path.stem}_{_safe_timestamp(timestamp)}.db"

    try:
        with sqlite3.connect(database_path) as source:
            with sqlite3.connect(backup_path) as destination:
                source.backup(destination)
    except sqlite3.Error as error:
        raise DatabaseBackupError(f"Could not back up SQLite database: {error}") from error

    return DatabaseBackupResult(
        source_path=database_path,
        backup_path=backup_path,
        created_at=timestamp,
        size_bytes=backup_path.stat().st_size,
    )


def _safe_timestamp(value: str) -> str:
    normalized = value.replace("+00:00", "Z")
    return re.sub(r"[^0-9A-Za-z]+", "", normalized)
