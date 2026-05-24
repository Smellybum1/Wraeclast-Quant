from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.site_bundle import SiteBundleResult

console = Console(width=260)


def print_site_bundle_error(error: str) -> None:
    console.print(error)


def print_site_bundle_result(result: SiteBundleResult) -> None:
    table = Table(title="Local Site Bundle")
    table.add_column("Artifact")
    table.add_column("Path")
    table.add_row("Bundle directory", str(result.bundle_dir))
    table.add_row("Archive", str(result.archive_path))
    table.add_row("Files", ", ".join(result.files))
    table.add_row("Generated", result.generated_at)
    console.print(table)
    console.print("Bundle is local-only. No publishing, hosting, or network requests were performed.")
