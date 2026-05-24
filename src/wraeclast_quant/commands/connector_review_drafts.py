from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_review_prep_rendering import print_connector_review_prep
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    build_connector_review_draft,
    prepare_connector_review_workspace,
    write_connector_review_draft,
)
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-draft")
    def connector_draft(
        resource: str = typer.Option(..., "--resource", help="Resource id or name from RESOURCES.md."),
        access_method: str = typer.Option(..., "--access-method", help="api, rss, download, or manual-export."),
        output_path: Path = typer.Option(..., "--output-path", help="Local connector review JSON draft path."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = build_connector_review_draft(
                resource_name=resource,
                access_method=access_method,
                resources=load_resources(resources_path),
            )
            written_path = write_connector_review_draft(review, output_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        console.print(f"Wrote connector review draft to {written_path}")
        console.print(
            "Draft is not approval. Review source terms and API/robots policy, then run "
            "wq connector-check before planning implementation."
        )

    @app.command("connector-review-prep")
    def connector_review_prep(
        resource: str = typer.Option(..., "--resource", help="Resource id or name from RESOURCES.md."),
        access_method: str = typer.Option(..., "--access-method", help="api, rss, download, or manual-export."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        output_dir: Path = typer.Option(Path("examples/reviews"), "--output-dir"),
    ) -> None:
        try:
            prep = prepare_connector_review_workspace(
                resource_name=resource,
                access_method=access_method,
                resources=load_resources(resources_path),
                output_dir=output_dir,
            )
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_connector_review_prep(prep)
