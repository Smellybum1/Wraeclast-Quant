from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console(width=260)


def print_site_contract_result(written_path: Path, payload: dict[str, Any]) -> None:
    readiness = payload["publish_readiness"]

    table = Table(title="Public Site Contract")
    table.add_column("Field")
    table.add_column("Value", no_wrap=False)
    table.add_row("Readiness", "ready" if readiness["ready"] else "not ready")
    table.add_row("Output path", str(written_path))
    table.add_row("Schema version", str(payload["schema_version"]))
    table.add_row("Latest database run", str(payload["latest_database_run_id"] or "none"))
    table.add_row("Bundle run", str(payload["artifact_run_ids"]["bundle"] or "none"))
    table.add_row("Public intel run", str(payload["artifact_run_ids"]["public_intel"] or "none"))
    table.add_row("Static site run", str(payload["artifact_run_ids"]["static_site"] or "none"))
    table.add_row("Blockers", "\n".join(readiness["blockers"]) if readiness["blockers"] else "None")
    console.print(table)
    console.print(
        "Site contract is local-only. It did not upload, host, fetch, publish, or modify RESOURCES.md."
    )
