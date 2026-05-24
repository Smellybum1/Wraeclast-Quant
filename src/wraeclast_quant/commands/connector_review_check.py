from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_check_workflow import build_connector_check_result
from wraeclast_quant.commands.connector_check_rendering import print_connector_check


def register(app: typer.Typer) -> None:
    @app.command("connector-check")
    def connector_check(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        result = build_connector_check_result(review_path, resources_path)
        print_connector_check(result)

        if result.ready:
            console.print("Connector review is ready for source-specific implementation planning.")
            return

        raise typer.Exit(code=1)
