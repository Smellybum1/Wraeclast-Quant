from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_approval_rendering import (
    print_connector_approval_helper,
    print_connector_approval_patch,
)
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    connector_approval_helper,
    connector_approval_patch,
    load_connector_review,
    write_connector_approval_patch,
)
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    register_helper(app)
    register_patch(app)


def register_helper(app: typer.Typer) -> None:
    @app.command("connector-approval-helper")
    def connector_approval_helper_command(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        result = connector_approval_helper(review, load_resources(resources_path))
        print_connector_approval_helper(result)


def register_patch(app: typer.Typer) -> None:
    @app.command("connector-approval-patch")
    def connector_approval_patch_command(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        output_path: Path = typer.Option(..., "--output-path", help="Local unified diff output path."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
            resources_markdown = resources_path.read_text(encoding="utf-8")
            resources = load_resources(resources_path)
            result = connector_approval_patch(
                review,
                resources,
                resources_markdown,
                str(resources_path),
            )
            if result.patch_available:
                written_path = write_connector_approval_patch(
                    review,
                    resources,
                    resources_markdown,
                    output_path,
                    str(resources_path),
                )
            else:
                written_path = None
        except OSError as error:
            raise typer.BadParameter(f"Could not read resources file: {error}") from error
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_connector_approval_patch(result, written_path)
        if not result.patch_available and result.blockers:
            raise typer.Exit(code=1)
