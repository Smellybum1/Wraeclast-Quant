from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.publish_check import (
    check_publish_readiness,
    publish_check_payload,
)
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
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
