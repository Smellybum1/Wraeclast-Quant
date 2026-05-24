from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_candidates_rendering import print_connector_candidates
from wraeclast_quant.config.connector_candidates import connector_candidates
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-candidates")
    def connector_candidate_report(
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
    ) -> None:
        candidates = connector_candidates(load_resources(resources_path), limit=limit)
        print_connector_candidates(candidates)
