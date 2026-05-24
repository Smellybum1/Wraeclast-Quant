from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("validate-intel")
    def validate_intel(
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
    ) -> None:
        try:
            result = validate_public_intel_file(intel_path)
        except PublicIntelContractError as error:
            raise typer.BadParameter(str(error)) from error

        table = Table(title="Public Intel Contract Validation")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Path", str(result.path))
        table.add_row("Valid", "yes" if result.valid else "no")
        table.add_row("Schema version", result.schema_version)
        table.add_row("Latest run", str(result.latest_run_id or "none"))
        table.add_row("Top opportunities", str(result.top_opportunities_count))
        table.add_row("Alerts", str(result.alerts_count))
        table.add_row("Errors", "\n".join(result.errors) if result.errors else "None")
        console.print(table)
        if not result.valid:
            raise typer.Exit(code=1)
        console.print("Public intel export matches the local derived-only contract.")
