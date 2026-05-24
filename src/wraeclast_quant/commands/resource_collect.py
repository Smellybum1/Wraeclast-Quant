from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.collectors.registry import collector_for
from wraeclast_quant.config.resources_loader import load_resources

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def collect(
        dry_run: bool = typer.Option(False, "--dry-run", help="Preview collectors without fetching."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        resources = load_resources(resources_path)
        table = Table(title="Configured Resources")
        for column in ["Source", "Type", "Priority", "Allowed Use", "URL", "Collector", "Status"]:
            table.add_column(column, no_wrap=True)

        for resource in resources:
            collector = collector_for(resource)
            result = collector.collect(dry_run=dry_run)
            url = resource.url if len(resource.url) <= 60 else f"{resource.url[:57]}..."
            table.add_row(
                resource.name,
                resource.type,
                resource.priority,
                resource.allowed_use,
                url,
                result.collector,
                result.status,
            )
        console.print(table)
