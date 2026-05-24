from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.config.compliance import assess_resources
from wraeclast_quant.config.resources_loader import load_resources
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.reports.public_intel import (
    DEFAULT_PUBLIC_INTEL_PATH,
    build_public_intel,
    write_public_intel,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
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
