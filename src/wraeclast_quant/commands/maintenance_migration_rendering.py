from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.storage.migration_models import MigrationReadinessResult
from wraeclast_quant.storage.models import RunProvenanceRecord

console = Console(width=260)


def print_migration_readiness(result: MigrationReadinessResult) -> None:
    table = Table(title="SQLite Migration Readiness")
    table.add_column("Check")
    table.add_column("Status", no_wrap=True)
    table.add_column("Details", no_wrap=False)
    for row in result.checks:
        table.add_row(row.check, row.status, row.details)
    console.print(table)
    console.print("Migration readiness is read-only. It did not create backups, mutate SQLite, or write files.")


def print_run_provenance(provenance: RunProvenanceRecord) -> None:
    table = Table(title=f"Run Provenance - Run #{provenance.run_id}")
    table.add_column("Field")
    table.add_column("Value", no_wrap=False)
    table.add_row("Run", str(provenance.run_id))
    table.add_row("Source kind", provenance.source_kind)
    table.add_row("Resource", provenance.resource_name)
    table.add_row("Connector", provenance.connector_id)
    table.add_row("Access method", provenance.access_method)
    table.add_row("Created", provenance.created_at)
    table.add_row("Metadata keys", ", ".join(sorted(provenance.metadata)))
    for key in sorted(provenance.metadata):
        table.add_row(key, str(provenance.metadata[key]))
    console.print(table)
    console.print("Run provenance is local-only and read-only. No files were written.")
