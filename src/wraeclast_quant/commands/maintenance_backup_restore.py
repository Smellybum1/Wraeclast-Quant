from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.backups import (
    DatabaseBackupError,
    build_restore_guidance,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH

console = Console(width=260)


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

        table = Table(title="SQLite Restore Helper")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Backup", str(guidance.backup_path))
        table.add_row("Target database", str(guidance.database_path))
        table.add_row("Target exists", "yes" if guidance.target_exists else "no")
        table.add_row("Target parent exists", "yes" if guidance.target_parent_exists else "no")
        table.add_row("Backup size bytes", str(guidance.backup_size_bytes))
        table.add_row("Latest run", str(guidance.latest_run_id or "none"))
        table.add_row("Latest source", guidance.latest_run_source_mode or "")
        table.add_row("Latest items", str(guidance.latest_run_item_count or 0))
        console.print(table)
        console.print("Manual PowerShell restore command:")
        console.print(guidance.powershell_command)
        console.print("Restore helper is read-only. It verified the backup and wrote no files.")
