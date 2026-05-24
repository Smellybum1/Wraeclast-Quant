from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_backup_create_rendering import (
    print_backup_created,
    print_no_database_to_back_up,
)
from wraeclast_quant.storage.backups import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    backup_database,
    verify_database_backup,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command("backup-db")
    def backup_db(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        output_dir: Path = typer.Option(DEFAULT_BACKUP_DIR, "--output-dir"),
    ) -> None:
        try:
            result = backup_database(database_path=database_path, output_dir=output_dir)
            verification = verify_database_backup(result.backup_path) if result is not None else None
        except DatabaseBackupError as error:
            raise typer.BadParameter(str(error)) from error

        if result is None:
            print_no_database_to_back_up()
            return

        if verification is None:
            raise typer.BadParameter("Backup verification did not run.")

        print_backup_created(result, verification)
