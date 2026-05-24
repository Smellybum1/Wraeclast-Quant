from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.reports.site_contract import (
    DEFAULT_SITE_CONTRACT_PATH,
    write_site_contract,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("site-contract")
    def site_contract(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        output_path: Path = typer.Option(DEFAULT_SITE_CONTRACT_PATH, "--output-path"),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when site contract readiness fails."),
    ) -> None:
        written_path, payload = write_site_contract(
            database_path=database_path,
            bundle_dir=bundle_dir,
            output_path=output_path,
        )
        readiness = payload["publish_readiness"]

        table = Table(title="Public Site Contract")
        table.add_column("Field")
        table.add_column("Value", no_wrap=False)
        table.add_row("Readiness", "ready" if readiness["ready"] else "not ready")
        table.add_row("Output path", str(written_path))
        table.add_row("Schema version", str(payload["schema_version"]))
        table.add_row("Latest database run", str(payload["latest_database_run_id"] or "none"))
        table.add_row("Bundle run", str(payload["artifact_run_ids"]["bundle"] or "none"))
        table.add_row("Public intel run", str(payload["artifact_run_ids"]["public_intel"] or "none"))
        table.add_row("Static site run", str(payload["artifact_run_ids"]["static_site"] or "none"))
        table.add_row("Blockers", "\n".join(readiness["blockers"]) if readiness["blockers"] else "None")
        console.print(table)
        console.print(
            "Site contract is local-only. It did not upload, host, fetch, publish, or modify RESOURCES.md."
        )
        if strict and not readiness["ready"]:
            raise typer.Exit(code=1)
