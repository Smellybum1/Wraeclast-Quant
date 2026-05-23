from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.snapshot_rendering import console, print_comparison
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison, compare_opportunities
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository


def register(app: typer.Typer) -> None:
    @app.command()
    def compare(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(5, "--limit", min=1, max=25),
    ) -> None:
        comparison = latest_comparison(database_path)
        if comparison is None:
            return
        print_comparison(comparison, limit=limit)


def latest_comparison(database_path: Path) -> SnapshotComparison | None:
    repository = SnapshotRepository(database_path)
    latest = repository.latest_run()
    if latest is None:
        console.print("No snapshots found.")
        return None

    previous = repository.previous_run_before(latest.id)
    if previous is None:
        console.print("No previous snapshot found for comparison.")
        return None

    return compare_opportunities(
        previous=repository.scored_opportunities_for_run(previous.id),
        latest=repository.scored_opportunities_for_run(latest.id),
        previous_run_id=previous.id,
        latest_run_id=latest.id,
    )
