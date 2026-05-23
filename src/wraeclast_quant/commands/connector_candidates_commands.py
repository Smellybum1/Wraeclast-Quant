from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.config.connector_candidates import connector_candidates
from wraeclast_quant.config.resources_loader import load_resources


def register(app: typer.Typer) -> None:
    @app.command("connector-candidates")
    def connector_candidate_report(
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
    ) -> None:
        candidates = connector_candidates(load_resources(resources_path), limit=limit)
        table = Table(title="Connector Review Candidates")
        for column in [
            "Source",
            "ID",
            "Type",
            "Allowed Use",
            "Priority",
            "Preflight",
            "Reason",
            "Suggested Access",
            "Draft Command",
        ]:
            table.add_column(column, no_wrap=column not in {"Reason", "Draft Command"})

        for candidate in candidates:
            resource = candidate.resource
            table.add_row(
                resource.name,
                resource.id,
                resource.type,
                resource.allowed_use,
                resource.priority,
                candidate.preflight.status,
                candidate.recommendation,
                candidate.suggested_access_method,
                candidate.draft_command or "Compliance-gated; do not draft from this command.",
            )
        console.print(table)
        console.print("Candidate report is advisory only. It does not approve automation or write files.")
