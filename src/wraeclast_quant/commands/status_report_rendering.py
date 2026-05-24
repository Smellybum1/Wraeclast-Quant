from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.commands.status_health_models import StatusHealthReport

console = Console(width=260)


def print_status_report(report: StatusHealthReport) -> None:
    table = Table(title="Wraeclast Quant Status")
    table.add_column("Check")
    table.add_column("Status", no_wrap=True)
    table.add_column("Details")
    for row in report.rows:
        table.add_row(row["check"], row["status"], row["details"])
    console.print(table)


def print_strict_status_failure(report: StatusHealthReport) -> None:
    console.print("Strict status failed: " + ", ".join(report.strict_failures))


__all__ = ["console", "print_status_report", "print_strict_status_failure"]
