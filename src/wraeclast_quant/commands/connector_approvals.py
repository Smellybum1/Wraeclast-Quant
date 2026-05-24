from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_approval_workflow import (
    build_connector_approval_helper_result,
    build_connector_approval_patch_result,
)
from wraeclast_quant.commands.connector_approval_rendering import (
    print_connector_approval_helper,
    print_connector_approval_patch,
)


def register(app: typer.Typer) -> None:
    register_helper(app)
    register_patch(app)


def register_helper(app: typer.Typer) -> None:
    @app.command("connector-approval-helper")
    def connector_approval_helper_command(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        result = build_connector_approval_helper_result(review_path, resources_path)
        print_connector_approval_helper(result)


def register_patch(app: typer.Typer) -> None:
    @app.command("connector-approval-patch")
    def connector_approval_patch_command(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        output_path: Path = typer.Option(..., "--output-path", help="Local unified diff output path."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        workflow = build_connector_approval_patch_result(
            review_path,
            output_path,
            resources_path,
        )
        print_connector_approval_patch(workflow.result, workflow.written_path)
        if not workflow.result.patch_available and workflow.result.blockers:
            raise typer.Exit(code=1)
