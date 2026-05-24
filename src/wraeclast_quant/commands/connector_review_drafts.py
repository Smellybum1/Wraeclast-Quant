from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.connector_review_draft_workflow import (
    prepare_connector_review_for_resource,
    write_connector_review_draft_for_resource,
)
from wraeclast_quant.commands.connector_review_prep_rendering import print_connector_review_prep


def register(app: typer.Typer) -> None:
    @app.command("connector-draft")
    def connector_draft(
        resource: str = typer.Option(..., "--resource", help="Resource id or name from RESOURCES.md."),
        access_method: str = typer.Option(..., "--access-method", help="api, rss, download, or manual-export."),
        output_path: Path = typer.Option(..., "--output-path", help="Local connector review JSON draft path."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        draft = write_connector_review_draft_for_resource(
            resource=resource,
            access_method=access_method,
            output_path=output_path,
            resources_path=resources_path,
        )

        console.print(f"Wrote connector review draft to {draft.written_path}")
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
        prep = prepare_connector_review_for_resource(
            resource=resource,
            access_method=access_method,
            resources_path=resources_path,
            output_dir=output_dir,
        )

        print_connector_review_prep(prep)
