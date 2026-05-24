from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.resource_collect_rendering import print_collect_results
from wraeclast_quant.collectors.registry import collector_for
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command()
    def collect(
        dry_run: bool = typer.Option(False, "--dry-run", help="Preview collectors without fetching."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        resources = load_resources(resources_path)
        rows = []
        for resource in resources:
            collector = collector_for(resource)
            result = collector.collect(dry_run=dry_run)
            rows.append((resource, result))
        print_collect_results(rows)
