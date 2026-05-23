from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from wraeclast_quant.storage.backup_models import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    DatabaseBackupListing,
    DatabaseRestoreGuidance,
)
from wraeclast_quant.storage.backup_verifier import verify_database_backup


def list_database_backups(
    backup_dir: Path = DEFAULT_BACKUP_DIR,
    limit: int = 10,
) -> list[DatabaseBackupListing]:
    if not backup_dir.exists():
        return []
    if not backup_dir.is_dir():
        raise DatabaseBackupError(f"Backup path is not a directory: {backup_dir}")

    backup_paths = sorted(
        (path for path in backup_dir.glob("*.db") if path.is_file()),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )[:limit]
    return [_backup_listing(path) for path in backup_paths]


def build_restore_guidance(
    backup_path: Path,
    database_path: Path,
) -> DatabaseRestoreGuidance:
    verification = verify_database_backup(backup_path)
    return DatabaseRestoreGuidance(
        backup_path=backup_path,
        database_path=database_path,
        backup_size_bytes=verification.size_bytes,
        latest_run_id=verification.latest_run_id,
        latest_run_source_mode=verification.latest_run_source_mode,
        latest_run_item_count=verification.latest_run_item_count,
        target_exists=database_path.exists(),
        target_parent_exists=database_path.parent.exists(),
        powershell_command=(
            "New-Item -ItemType Directory -Force -Path "
            f"{_quote_powershell_literal(database_path.parent)}; "
            "Copy-Item -LiteralPath "
            f"{_quote_powershell_literal(backup_path)} "
            "-Destination "
            f"{_quote_powershell_literal(database_path)} "
            "-Force"
        ),
    )


def _backup_listing(path: Path) -> DatabaseBackupListing:
    modified_at = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(
        timespec="seconds"
    )
    try:
        verification = verify_database_backup(path)
    except DatabaseBackupError as error:
        return DatabaseBackupListing(
            backup_path=path,
            modified_at=modified_at,
            size_bytes=path.stat().st_size,
            valid=False,
            analysis_run_count=None,
            latest_run_id=None,
            latest_run_source_mode=None,
            error=str(error),
        )

    return DatabaseBackupListing(
        backup_path=path,
        modified_at=modified_at,
        size_bytes=verification.size_bytes,
        valid=True,
        analysis_run_count=verification.analysis_run_count,
        latest_run_id=verification.latest_run_id,
        latest_run_source_mode=verification.latest_run_source_mode,
        error="",
    )


def _quote_powershell_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"
