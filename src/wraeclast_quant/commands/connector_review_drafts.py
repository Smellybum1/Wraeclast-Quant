from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands._connector_support import console
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

        table = Table(title="Connector Review Prep")
        table.add_column("Field")
        table.add_column("Value", no_wrap=False)
        table.add_row("Resource", prep.review.resource_name)
        table.add_row("Access method", prep.review.access_method)
        table.add_row("Review draft", str(prep.review_path))
        table.add_row("Checklist", str(prep.checklist_path))
        console.print(table)
        console.print("Next local commands:")
        for command in prep.next_commands:
            console.print(command, soft_wrap=True)
        console.print(
            "Review prep is local-only. It did not edit RESOURCES.md, fetch data, or approve a connector."
        )
