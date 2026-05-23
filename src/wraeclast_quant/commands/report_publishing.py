from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.publish_check import (
    DEFAULT_PUBLISH_HANDOFF_PATH,
    check_publish_readiness,
    publish_check_payload,
    write_publish_handoff,
)
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.reports.site_contract import (
    DEFAULT_SITE_CONTRACT_PATH,
    write_site_contract,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("publish-check")
    def publish_check(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when publishing readiness fails."),
        json_output: bool = typer.Option(False, "--json", help="Print publish readiness as JSON."),
    ) -> None:
        result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)
        if json_output:
            typer.echo(json.dumps(publish_check_payload(result), indent=2, sort_keys=True))
        else:
            table = Table(title="Local Publish Readiness")
            table.add_column("Check")
            table.add_column("Status", no_wrap=True)
            table.add_column("Details")
            for row in result.checks:
                table.add_row(row.check, row.status, row.details)
            console.print(table)
            console.print(f"Archive: {result.archive_path}")
            console.print("Files: " + (", ".join(result.files) if result.files else "None"))
            console.print(
                "Publish check is local-only. It did not upload, host, fetch, or modify files."
            )
        if strict and not result.ready:
            raise typer.Exit(code=1)

    @app.command("publish-handoff")
    def publish_handoff(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        output_path: Path = typer.Option(DEFAULT_PUBLISH_HANDOFF_PATH, "--output-path"),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when publishing readiness fails."),
    ) -> None:
        result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)
        written_path = write_publish_handoff(result, output_path)

        table = Table(title="Manual Publish Handoff")
        table.add_column("Field")
        table.add_column("Value", no_wrap=False)
        table.add_row("Readiness", "ready" if result.ready else "not ready")
        table.add_row("Output path", str(written_path))
        table.add_row("Archive", str(result.archive_path))
        table.add_row("Blockers", "\n".join(result.blockers) if result.blockers else "None")
        console.print(table)
        console.print(
            "Publish handoff is local-only. It did not upload, host, fetch, publish, or modify RESOURCES.md."
        )
        if strict and not result.ready:
            raise typer.Exit(code=1)

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
