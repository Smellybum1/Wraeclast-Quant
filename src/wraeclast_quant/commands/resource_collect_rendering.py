from __future__ import annotations

from rich.console import Console
from rich.table import Table

from wraeclast_quant.collectors.base import CollectionResult
from wraeclast_quant.config.resources_loader import Resource

console = Console(width=260)


def print_collect_results(rows: list[tuple[Resource, CollectionResult]]) -> None:
    table = Table(title="Configured Resources")
    for column in ["Source", "Type", "Priority", "Allowed Use", "URL", "Collector", "Status"]:
        table.add_column(column, no_wrap=True)

    for resource, result in rows:
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
