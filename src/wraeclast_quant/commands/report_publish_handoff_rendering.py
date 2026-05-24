from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.publish_check import PublishCheckResult

console = Console(width=260)


def print_publish_handoff_result(result: PublishCheckResult, written_path: Path) -> None:
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
