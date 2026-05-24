from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_plan_rendering import print_connector_plan
from wraeclast_quant.commands.connector_plan_workflow import build_connector_plan_result


def register(app: typer.Typer) -> None:
    @app.command("connector-plan")
    def connector_plan(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        workflow = build_connector_plan_result(review_path, resources_path)
        print_connector_plan(workflow.review, workflow.result)
        if workflow.result.plan is None:
            raise typer.Exit(code=1)
