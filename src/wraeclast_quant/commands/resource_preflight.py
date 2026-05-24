from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.resource_preflight_rendering import (
    print_preflight_assessments,
    print_preflight_summary,
)
from wraeclast_quant.config.preflight import assess_preflight_resources, summarize_preflight
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command()
    def preflight(
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        assessments = assess_preflight_resources(load_resources(resources_path))
        print_preflight_assessments(assessments)
        summary = summarize_preflight(assessments)
        print_preflight_summary(summary)
