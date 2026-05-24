from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.publish_check import PublishCheckResult

console = Console(width=260)


def print_publish_check_result(result: PublishCheckResult) -> None:
    table = Table(title="Local Publish Readiness")
    table.add_column("Check")
    table.add_column("Status", no_wrap=True)
    table.add_column("Details")
    for row in result.checks:
        table.add_row(row.check, row.status, row.details)
    console.print(table)
    console.print(f"Archive: {result.archive_path}")
    console.print("Files: " + (", ".join(result.files) if result.files else "None"))
    console.print("Publish check is local-only. It did not upload, host, fetch, or modify files.")
