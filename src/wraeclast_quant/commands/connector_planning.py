from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, load_connector_review
from wraeclast_quant.config.fetch_policy import build_fetch_plan
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-plan")
    def connector_plan(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        try:
            review = load_connector_review(review_path)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        result = build_fetch_plan(review, load_resources(resources_path))
        table = Table(title="Safe Fetch Plan")
        for column in [
            "Resource",
            "URL",
            "Access",
            "Cache Path",
            "TTL",
            "Rate Limit",
            "Min Interval",
            "Ready",
            "Blockers",
        ]:
            table.add_column(column, no_wrap=column not in {"URL", "Cache Path", "Blockers"})

        if result.plan is None:
            table.add_row(
                review.resource_name,
                "",
                review.access_method,
                "",
                str(review.cache_ttl_seconds),
                f"{review.rate_limit_per_minute:g}/min",
                "",
                "no",
                "\n".join(result.check.blockers),
            )
            console.print(table)
            raise typer.Exit(code=1)

        plan = result.plan
        table.add_row(
            plan.resource_name,
            plan.url,
            plan.access_method,
            str(plan.cache_path),
            str(plan.cache_ttl_seconds),
            f"{plan.rate_limit_per_minute:g}/min",
            f"{plan.min_seconds_between_requests:.2f}s",
            "yes",
            "None",
        )
        console.print(table)
        console.print("Fetch plan is local-only. No network requests were made and no files were written.")
