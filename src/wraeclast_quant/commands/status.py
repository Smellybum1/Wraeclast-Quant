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
from wraeclast_quant.storage.health import DatabaseHealthError, check_database_health
from wraeclast_quant.storage.schema import (
    REQUIRED_SQLITE_TABLES,
    SQLITE_SCHEMA_VERSION,
    SQLITE_TABLE_DESCRIPTIONS,
)

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("schema")
    def schema() -> None:
        table = Table(title=f"SQLite Schema Contract v{SQLITE_SCHEMA_VERSION}")
        table.add_column("Table")
        table.add_column("Required", no_wrap=True)
        table.add_column("Description")
        for table_name in sorted(REQUIRED_SQLITE_TABLES):
            table.add_row(
                table_name,
                "yes",
                SQLITE_TABLE_DESCRIPTIONS.get(table_name, ""),
            )
        console.print(table)
        console.print("Schema inspection is read-only. No database was opened or written.")

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

    @app.command("db-check")
    def db_check(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        try:
            result = check_database_health(database_path)
        except DatabaseHealthError as error:
            raise typer.BadParameter(str(error)) from error

        if result is None:
            console.print("No database found.")
            return

        table = Table(title="SQLite Database Check")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Database", str(result.database_path))
        table.add_row("Overall", "ok" if result.ok else "needs attention")
        table.add_row("Schema version", result.schema_version)
        table.add_row("Integrity", "ok" if result.integrity_ok else "failed")
        table.add_row("Integrity message", result.integrity_message)
        table.add_row("Required tables", "ok" if result.schema_ok else "missing")
        table.add_row("Required table names", ", ".join(result.required_tables))
        table.add_row("Missing tables", ", ".join(result.missing_tables))
        table.add_row("Size bytes", str(result.size_bytes))
        table.add_row("Analysis runs", _optional_int(result.analysis_run_count))
        table.add_row("Scored opportunities", _optional_int(result.scored_opportunity_count))
        table.add_row("Report artifacts", _optional_int(result.report_artifact_count))
        table.add_row("Recommendation outcomes", _optional_int(result.recommendation_outcome_count))
        table.add_row("Latest run", _optional_int(result.latest_run_id, none_value="none"))
        table.add_row("Latest source", result.latest_run_source_mode or "")
        table.add_row("Latest items", _optional_int(result.latest_run_item_count))
        table.add_row("Latest created", result.latest_run_created_at or "")
        console.print(table)
        console.print("Database check is read-only. No files were written.")


def _optional_int(value: int | None, none_value: str = "") -> str:
    return none_value if value is None else str(value)
