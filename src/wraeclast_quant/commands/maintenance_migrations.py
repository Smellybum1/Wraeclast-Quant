from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.migrations import (
    check_migration_readiness,
    migration_readiness_payload,
)
from wraeclast_quant.storage.repositories import SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("migration-readiness")
    def migration_readiness(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        backup_dir: Path = typer.Option(DEFAULT_BACKUP_DIR, "--backup-dir"),
        json_output: bool = typer.Option(False, "--json", help="Print migration readiness as JSON."),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when migration readiness fails."),
    ) -> None:
        result = check_migration_readiness(database_path=database_path, backup_dir=backup_dir)
        if json_output:
            typer.echo(json.dumps(migration_readiness_payload(result), indent=2, sort_keys=True))
        else:
            table = Table(title="SQLite Migration Readiness")
            table.add_column("Check")
            table.add_column("Status", no_wrap=True)
            table.add_column("Details", no_wrap=False)
            for row in result.checks:
                table.add_row(row.check, row.status, row.details)
            console.print(table)
            console.print(
                "Migration readiness is read-only. It did not create backups, mutate SQLite, or write files."
            )
        if strict and not result.ready:
            raise typer.Exit(code=1)

    @app.command("run-provenance")
    def run_provenance(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1, help="Analysis run id. Defaults to the latest run."),
    ) -> None:
        repository = SnapshotRepository(database_path)
        provenance = (
            repository.run_provenance(run_id)
            if run_id is not None
            else repository.latest_run_provenance()
        )
        if provenance is None:
            if run_id is None:
                console.print("No run provenance found.")
                return
            console.print(f"No run provenance found for run #{run_id}.")
            return

        table = Table(title=f"Run Provenance - Run #{provenance.run_id}")
        table.add_column("Field")
        table.add_column("Value", no_wrap=False)
        table.add_row("Run", str(provenance.run_id))
        table.add_row("Source kind", provenance.source_kind)
        table.add_row("Resource", provenance.resource_name)
        table.add_row("Connector", provenance.connector_id)
        table.add_row("Access method", provenance.access_method)
        table.add_row("Created", provenance.created_at)
        table.add_row("Metadata keys", ", ".join(sorted(provenance.metadata)))
        for key in sorted(provenance.metadata):
            table.add_row(key, str(provenance.metadata[key]))
        console.print(table)
        console.print("Run provenance is local-only and read-only. No files were written.")
