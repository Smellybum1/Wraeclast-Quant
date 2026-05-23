from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.backups import (
    DEFAULT_BACKUP_DIR,
    DatabaseBackupError,
    list_database_backups,
    verify_database_backup,
)

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("verify-backup")
    def verify_backup(
        backup_path: Path = typer.Option(..., "--backup-path", help="Local SQLite backup file."),
    ) -> None:
        try:
            result = verify_database_backup(backup_path)
        except DatabaseBackupError as error:
            raise typer.BadParameter(str(error)) from error

        table = Table(title="SQLite Backup Verification")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Backup", str(result.backup_path))
        table.add_row("Schema version", result.schema_version)
        table.add_row("Required table names", ", ".join(result.required_tables))
        table.add_row("Size bytes", str(result.size_bytes))
        table.add_row("Analysis runs", str(result.analysis_run_count))
        table.add_row("Scored opportunities", str(result.scored_opportunity_count))
        table.add_row("Report artifacts", str(result.report_artifact_count))
        table.add_row("Recommendation outcomes", str(result.recommendation_outcome_count))
        table.add_row("Latest run", str(result.latest_run_id or "none"))
        table.add_row("Latest source", result.latest_run_source_mode or "")
        table.add_row("Latest items", str(result.latest_run_item_count or 0))
        table.add_row("Latest created", result.latest_run_created_at or "")
        console.print(table)
        console.print("Backup verification is read-only. No files were written.")

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
            console.print("No database backups found.")
            return

        table = Table(title="Local SQLite Backups")
        for column in [
            "Status",
            "Backup",
            "Modified",
            "Size",
            "Runs",
            "Latest Run",
            "Latest Source",
            "Error",
        ]:
            table.add_column(column, no_wrap=column not in {"Backup", "Error"})

        for listing in listings:
            table.add_row(
                "valid" if listing.valid else "invalid",
                str(listing.backup_path),
                listing.modified_at,
                str(listing.size_bytes),
                "" if listing.analysis_run_count is None else str(listing.analysis_run_count),
                "" if listing.latest_run_id is None else str(listing.latest_run_id),
                listing.latest_run_source_mode or "",
                listing.error,
            )
        console.print(table)
        console.print("Backup listing is read-only. No files were written.")
