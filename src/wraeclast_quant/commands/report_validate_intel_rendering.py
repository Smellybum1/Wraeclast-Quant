from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.public_intel_contract import PublicIntelValidationResult

console = Console(width=260)


def print_public_intel_validation(result: PublicIntelValidationResult) -> None:
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


def print_public_intel_validation_success() -> None:
    console.print("Public intel export matches the local derived-only contract.")
