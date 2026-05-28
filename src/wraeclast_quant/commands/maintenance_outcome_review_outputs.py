from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.maintenance_outcome_review_context import (
    read_review_queue_context,
)
from wraeclast_quant.reports.review_queue_commands import record_outcomes_dry_run_command
from wraeclast_quant.reports.review_queue_decisions import (
    write_review_queue_decisions_template,
)
from wraeclast_quant.reports.review_queue_worksheet import write_review_queue_worksheet
from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord


def write_review_queue_outputs(
    *,
    output_path: Path | None,
    decisions_output_path: Path | None,
    context_path: Path | None,
    database_path: object | None = None,
    run: AnalysisRunRecord,
    opportunities: list[StoredOpportunityRecord],
) -> None:
    if output_path is not None:
        context_markdown = read_review_queue_context(context_path) if context_path is not None else None
        write_review_queue_worksheet(
            output_path,
            run_id=run.id,
            source_mode=run.source_mode,
            opportunities=opportunities,
            context_markdown=context_markdown,
            database_path=database_path,
        )
        typer.echo(f"Wrote review queue worksheet to {output_path}")
    if decisions_output_path is not None:
        try:
            write_review_queue_decisions_template(
                decisions_output_path,
                run_id=run.id,
                opportunities=opportunities,
            )
        except ValueError as error:
            typer.echo(str(error), err=True)
            raise typer.Exit(code=1) from error
        typer.echo(f"Wrote outcome decisions template to {decisions_output_path}")
        typer.echo(
            f"Next: fill outcome labels, then run "
            f"{record_outcomes_dry_run_command(str(decisions_output_path), database_path=database_path)}."
        )


__all__ = ["write_review_queue_outputs"]
