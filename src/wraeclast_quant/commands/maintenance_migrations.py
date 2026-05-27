from __future__ import annotations

import json
from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_migration_rendering import (
    console,
    print_migration_readiness,
    print_run_provenance,
)
from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.migrations import (
    check_migration_readiness,
    migration_readiness_payload,
)
from wraeclast_quant.storage.repositories import SnapshotRepository


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
            print_migration_readiness(result)
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
                run = repository.latest_run()
                if run is None:
                    console.print("No run provenance found.")
                    return
                console.print(_missing_run_provenance_message(run.id, run.source_mode))
                return
            run = repository.analysis_run(run_id)
            source_mode = run.source_mode if run is not None else None
            console.print(_missing_run_provenance_message(run_id, source_mode))
            return

        print_run_provenance(provenance)


def _missing_run_provenance_message(run_id: int, source_mode: str | None) -> str:
    if source_mode is None:
        return f"No run provenance found for run #{run_id}."
    lines = [
        f"No run provenance found for run #{run_id} (source mode: {source_mode}).",
        "Run provenance is local-only and read-only; no files were written.",
    ]
    if source_mode == "manual-import":
        lines.append(
            "This run may predate manual-import provenance recording. "
            "Future wq daily --input-path runs record path-safe local input metadata."
        )
    return "\n".join(lines)
