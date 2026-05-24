from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.config.preflight import assess_preflight_resources, summarize_preflight
from wraeclast_quant.config.resources_loader import load_resources

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def preflight(
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
    ) -> None:
        assessments = assess_preflight_resources(load_resources(resources_path))
        table = Table(title="Connector Preflight")
        for column in [
            "Source",
            "Type",
            "Allowed Use",
            "Collector",
            "Status",
            "Automation",
            "Reason",
            "Next Step",
        ]:
            table.add_column(column, no_wrap=column not in {"Reason", "Next Step"})

        for assessment in assessments:
            resource = assessment.resource
            table.add_row(
                resource.name,
                resource.type,
                resource.allowed_use,
                assessment.collector,
                assessment.status,
                "yes" if assessment.automation_eligible else "no",
                assessment.reason,
                assessment.next_step,
            )
        console.print(table)

        summary = summarize_preflight(assessments)
        summary_table = Table(title="Preflight Summary")
        summary_table.add_column("Metric")
        summary_table.add_column("Count", justify="right")
        for label, count in [
            ("total", summary.total),
            ("eligible", summary.eligible),
            ("manual-review", summary.manual_review),
            ("needs-review", summary.needs_review),
            ("blocked", summary.blocked),
            ("discord-gated", summary.discord_gated),
            ("placeholder-only", summary.placeholder_only),
        ]:
            summary_table.add_row(label, str(count))
        console.print(summary_table)
