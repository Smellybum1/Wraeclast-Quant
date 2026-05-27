from __future__ import annotations

import json
from pathlib import Path

import typer

from wraeclast_quant.commands.status_health import build_status_report
from wraeclast_quant.commands.status_report_rendering import (
    print_status_report,
    print_strict_status_failure,
)
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.reports.stash_ninja_watchlist import DEFAULT_STASH_NINJA_WATCHLIST_PATH
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.storage.backups import DEFAULT_BACKUP_DIR, DatabaseBackupError
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.health import DatabaseHealthError


def register(app: typer.Typer) -> None:
    @app.command()
    def status(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        brief_path: Path = typer.Option(Path("data/processed/market_brief.md"), "--brief-path"),
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        stash_ninja_path: Path = typer.Option(
            DEFAULT_STASH_NINJA_WATCHLIST_PATH,
            "--stash-ninja-path",
        ),
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
                stash_ninja_path=stash_ninja_path,
                backup_dir=backup_dir,
            )
        except DatabaseBackupError as error:
            raise typer.BadParameter(str(error)) from error
        except DatabaseHealthError as error:
            raise typer.BadParameter(str(error)) from error

        if json_output:
            typer.echo(json.dumps(report.json_payload(strict=strict), indent=2, sort_keys=True))
        else:
            print_status_report(report)

        if strict and report.strict_failures:
            if not json_output:
                print_strict_status_failure(report)
            raise typer.Exit(1)


__all__ = ["register"]
