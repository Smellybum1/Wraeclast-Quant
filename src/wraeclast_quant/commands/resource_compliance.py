from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import load_resources

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def compliance(
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        assessments = assess_resources(load_resources(resources_path))
        table = Table(title="Resource Compliance")
        for column in [
            "Source",
            "Type",
            "Allowed Use",
            "Collector",
            "Status",
            "Automation",
            "Reason",
        ]:
            table.add_column(column, no_wrap=column != "Reason")

        for assessment in assessments:
            resource = assessment.resource
            table.add_row(
                resource.name,
                resource.type,
                resource.allowed_use,
                resource.collector or "placeholder",
                assessment.status,
                "yes" if assessment.automation_eligible else "no",
                assessment.reason,
            )
        console.print(table)
