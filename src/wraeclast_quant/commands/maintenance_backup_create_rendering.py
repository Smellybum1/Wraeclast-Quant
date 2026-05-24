from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.backups import DatabaseBackupResult, DatabaseBackupVerification

console = Console(width=260)


def print_no_database_to_back_up() -> None:
    console.print("No database found to back up.")


def print_backup_created(
    result: DatabaseBackupResult,
    verification: DatabaseBackupVerification,
) -> None:
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
