from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_backup_restore_rendering import print_restore_guidance
from wraeclast_quant.storage.backups import (
    DatabaseBackupError,
    build_restore_guidance,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command("restore-helper")
    def restore_helper(
        backup_path: Path = typer.Option(..., "--backup-path", help="Local SQLite backup file."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        try:
            guidance = build_restore_guidance(
                backup_path=backup_path,
                database_path=database_path,
            )
        except DatabaseBackupError as error:
            raise typer.BadParameter(str(error)) from error

        print_restore_guidance(guidance)
