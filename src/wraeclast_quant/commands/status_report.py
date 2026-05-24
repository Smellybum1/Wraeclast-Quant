from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.commands.status_health import build_status_report
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR, DatabaseBackupError
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.health import DatabaseHealthError

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def status(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        brief_path: Path = typer.Option(Path("data/processed/market_brief.md"), "--brief-path"),
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        backup_dir: Path = typer.Option(DEFAULT_BACKUP_DIR, "--backup-dir"),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when a health check needs attention."),
        json_output: bool = typer.Option(False, "--json", help="Print status as machine-readable JSON."),
    ) -> None:
        try:
            report = build_status_report(
                database_path=database_path,
                resources_path=resources_path,
                brief_path=brief_path,
                intel_path=intel_path,
                site_dir=site_dir,
                bundle_dir=bundle_dir,
                backup_dir=backup_dir,
            )
        except DatabaseBackupError as error:
            raise typer.BadParameter(str(error)) from error
        except DatabaseHealthError as error:
            raise typer.BadParameter(str(error)) from error

        if json_output:
            typer.echo(json.dumps(report.json_payload(strict=strict), indent=2, sort_keys=True))
        else:
            table = Table(title="Wraeclast Quant Status")
            table.add_column("Check")
            table.add_column("Status", no_wrap=True)
            table.add_column("Details")
            for row in report.rows:
                table.add_row(row["check"], row["status"], row["details"])
            console.print(table)

        if strict and report.strict_failures:
            if not json_output:
                console.print("Strict status failed: " + ", ".join(report.strict_failures))
            raise typer.Exit(1)
