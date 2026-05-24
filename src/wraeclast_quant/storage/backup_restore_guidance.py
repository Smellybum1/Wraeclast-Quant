from __future__ import annotations

from pathlib import Path

from wraeclast_quant.storage.backup_models import DatabaseRestoreGuidance
from wraeclast_quant.storage.backup_verifier import verify_database_backup


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
            f"{quote_powershell_literal(database_path.parent)}; "
            "Copy-Item -LiteralPath "
            f"{quote_powershell_literal(backup_path)} "
            "-Destination "
            f"{quote_powershell_literal(database_path)} "
            "-Force"
        ),
    )


def quote_powershell_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


__all__ = ["build_restore_guidance", "quote_powershell_literal"]
