from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.intake_analysis_workflow import (
    record_analysis_run,
    sample_analysis_opportunities,
)
from wraeclast_quant.commands.intake_rendering import console, print_opportunities
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command()
    def analyze(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        opportunities = sample_analysis_opportunities(sample_data)
        print_opportunities("Scored Opportunities", opportunities)
        run = record_analysis_run(database_path, opportunities)
        console.print(f"Recorded analysis run #{run.id} to {database_path}")
