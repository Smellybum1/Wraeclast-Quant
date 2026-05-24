from __future__ import annotations

from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_policy import ConnectorReviewPrepResult


def print_connector_review_prep(prep: ConnectorReviewPrepResult) -> None:
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
    console.print("Review prep is local-only. It did not edit RESOURCES.md, fetch data, or approve a connector.")
