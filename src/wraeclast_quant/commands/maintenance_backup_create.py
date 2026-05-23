from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.backups import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    backup_database,
    verify_database_backup,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH

console = Console(width=260)


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
            console.print("No database found to back up.")
            return

        if verification is None:
            raise typer.BadParameter("Backup verification did not run.")

        table = Table(title="Local SQLite Backup")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Source", str(result.source_path))
        table.add_row("Backup", str(result.backup_path))
        table.add_row("Created", result.created_at)
        table.add_row("Verified", "yes")
        table.add_row("Schema version", verification.schema_version)
        table.add_row("Size bytes", str(result.size_bytes))
        table.add_row("Analysis runs", str(verification.analysis_run_count))
        table.add_row("Latest run", str(verification.latest_run_id or "none"))
        table.add_row("Latest source", verification.latest_run_source_mode or "")
        console.print(table)
        console.print(
            "Backup is local-only and was verified after creation. "
            "No network requests or external publishing were performed."
        )
