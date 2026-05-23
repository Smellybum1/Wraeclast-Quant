from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    check_connector_review,
    load_connector_review,
)
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-check")
    def connector_check(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        result = check_connector_review(review, load_resources(resources_path))
        table = Table(title="Connector Review Check")
        for column in [
            "Resource",
            "Access Method",
            "Preflight",
            "Ready",
            "Cache TTL",
            "Rate Limit",
            "Blockers",
        ]:
            table.add_column(column, no_wrap=column != "Blockers")

        preflight_status = result.preflight.status if result.preflight is not None else "missing"
        table.add_row(
            review.resource_name,
            review.access_method,
            preflight_status,
            "yes" if result.ready else "no",
            str(review.cache_ttl_seconds),
            f"{review.rate_limit_per_minute:g}/min",
            "\n".join(result.blockers) if result.blockers else "None",
        )
        console.print(table)

        if result.ready:
            console.print("Connector review is ready for source-specific implementation planning.")
            return

        raise typer.Exit(code=1)
