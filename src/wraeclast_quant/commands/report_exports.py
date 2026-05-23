from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import load_resources
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.reports.market_brief import write_market_brief
from wraeclast_quant.reports.public_intel import (
    DEFAULT_PUBLIC_INTEL_PATH,
    build_public_intel,
    write_public_intel,
)
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def report(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
    ) -> None:
        opportunities = _sample_opportunities(sample_data)
        repository = SnapshotRepository(database_path)
        run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
        previous = repository.previous_run_before(run.id)
        repository.save_scored_opportunities(run.id, opportunities)
        comparison = None
        if previous is not None:
            comparison = compare_opportunities(
                previous=repository.scored_opportunities_for_run(previous.id),
                latest=repository.scored_opportunities_for_run(run.id),
                previous_run_id=previous.id,
                latest_run_id=run.id,
            )
        output_path = write_market_brief(opportunities, comparison=comparison)
        repository.save_report_artifact(run.id, output_path)
        console.print(f"Wrote market brief to {output_path}")
        console.print(f"Recorded report artifact for analysis run #{run.id} to {database_path}")

    @app.command("export")
    def export_intel(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        output_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--output-path"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
        watch_threshold: float = typer.Option(55.0, "--watch-threshold", min=0, max=100),
        buy_threshold: float = typer.Option(75.0, "--buy-threshold", min=0, max=100),
        big_delta: float = typer.Option(10.0, "--big-delta", min=0, max=100),
    ) -> None:
        alert_settings = _alert_settings(watch_threshold, buy_threshold, big_delta)
        resources = load_resources(resources_path)
        payload = build_public_intel(
            repository=SnapshotRepository(database_path),
            resources=resources,
            assessments=assess_resources(resources),
            limit=limit,
            alert_settings=alert_settings,
        )
        if payload is None:
            console.print("No snapshots found.")
            return

        written_path = write_public_intel(payload, output_path)
        console.print(
            f"Wrote public intel export for run #{payload['latest_run']['id']} to {written_path}"
        )


def _sample_opportunities(sample_data: bool):
    if not sample_data:
        raise typer.BadParameter("Only --sample-data is supported in the MVP.")
    return rank_opportunities(SAMPLE_ITEMS)


def _alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    try:
        return AlertRuleSettings(
            watch_threshold=watch_threshold,
            buy_threshold=buy_threshold,
            big_positive_delta=big_delta,
        )
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error
