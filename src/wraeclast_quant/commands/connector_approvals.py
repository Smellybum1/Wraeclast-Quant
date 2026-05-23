from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands._connector_support import console
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
        table = Table(title="Connector Approval Helper")
        for column in [
            "Resource",
            "ID",
            "Current Allowed Use",
            "Access",
            "Preflight",
            "Evidence Ready",
            "Connector Check",
            "Manual Approval Suggestion",
            "Reason / Blockers",
        ]:
            table.add_column(
                column,
                no_wrap=column not in {"Manual Approval Suggestion", "Reason / Blockers"},
            )

        resource = result.resource
        preflight_status = result.preflight.status if result.preflight is not None else "missing"
        blockers = "\n".join(result.blockers) if result.blockers else result.reason
        table.add_row(
            resource.name if resource is not None else review.resource_name,
            resource.id if resource is not None else "",
            resource.allowed_use if resource is not None else "",
            review.access_method,
            preflight_status,
            "yes" if result.evidence_ready else "no",
            "yes" if result.connector_check_ready else "no",
            result.approval_suggestion if result.suggestion_available else "None",
            blockers if result.blockers else result.reason,
        )
        console.print(table)

        if result.suggestion_available:
            console.print("Manual approval suggestion:")
            console.print(result.approval_suggestion)
            console.print("This command is read-only. Manually edit RESOURCES.md only after approval.")
        else:
            console.print(result.reason)


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

        table = Table(title="Connector Approval Patch Preview")
        table.add_column("Field")
        table.add_column("Value", no_wrap=False)
        table.add_row("Resource", review.resource_name)
        table.add_row("Patch available", "yes" if result.patch_available else "no")
        table.add_row("Output path", str(written_path) if written_path is not None else "None")
        table.add_row("Reason", result.reason)
        table.add_row("Blockers", "\n".join(result.blockers) if result.blockers else "None")
        console.print(table)
        console.print(
            "Approval patch is advisory only. It did not edit RESOURCES.md, fetch data, or approve a connector."
        )
        if not result.patch_available and result.blockers:
            raise typer.Exit(code=1)
