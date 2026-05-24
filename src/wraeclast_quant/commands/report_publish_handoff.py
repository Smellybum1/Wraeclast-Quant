from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.publish_check import (
    DEFAULT_PUBLISH_HANDOFF_PATH,
    check_publish_readiness,
    write_publish_handoff,
)
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH

console = Console(width=260)


def register(app: typer.Typer) -> None:
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
