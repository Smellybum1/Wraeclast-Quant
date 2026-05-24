from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.resource_compliance_rendering import print_compliance_assessments
from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command()
    def compliance(
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        assessments = assess_resources(load_resources(resources_path))
        print_compliance_assessments(assessments)
