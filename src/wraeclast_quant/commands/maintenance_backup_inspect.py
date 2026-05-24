from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_backup_inspect_rendering import (
    print_backup_listings,
    print_backup_verification,
    print_no_backups_found,
)
from wraeclast_quant.storage.backups import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    list_database_backups,
    verify_database_backup,
)


def register(app: typer.Typer) -> None:
    @app.command("verify-backup")
    def verify_backup(
        backup_path: Path = typer.Option(..., "--backup-path", help="Local SQLite backup file."),
    ) -> None:
        try:
            result = verify_database_backup(backup_path)
        except DatabaseBackupError as error:
            raise typer.BadParameter(str(error)) from error

        print_backup_verification(result)

    @app.command("backups")
    def backups(
        backup_dir: Path = typer.Option(DEFAULT_BACKUP_DIR, "--backup-dir"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
    ) -> None:
        try:
            listings = list_database_backups(backup_dir=backup_dir, limit=limit)
        except DatabaseBackupError as error:
            raise typer.BadParameter(str(error)) from error

        if not listings:
            print_no_backups_found()
            return

        print_backup_listings(listings)
