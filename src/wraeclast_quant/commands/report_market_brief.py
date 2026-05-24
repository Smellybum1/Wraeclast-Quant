from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.commands.report_market_brief_workflow import (
    sample_report_opportunities,
    write_sample_market_brief_report,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def report(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        opportunities = sample_report_opportunities(sample_data)
        result = write_sample_market_brief_report(database_path, opportunities)
        console.print(f"Wrote market brief to {result.output_path}")
        console.print(f"Recorded report artifact for analysis run #{result.run.id} to {database_path}")
