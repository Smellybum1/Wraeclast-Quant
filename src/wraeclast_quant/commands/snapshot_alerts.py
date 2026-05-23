from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.snapshot_compare import latest_comparison
from wraeclast_quant.commands.snapshot_rendering import print_alert_candidates
from wraeclast_quant.intelligence.alerts import AlertRuleSettings, generate_alerts
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command()
    def alerts(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
        watch_threshold: float = typer.Option(55.0, "--watch-threshold", min=0, max=100),
        buy_threshold: float = typer.Option(75.0, "--buy-threshold", min=0, max=100),
        big_delta: float = typer.Option(10.0, "--big-delta", min=0, max=100),
    ) -> None:
        alert_settings = _alert_settings(watch_threshold, buy_threshold, big_delta)
        comparison = latest_comparison(database_path)
        if comparison is None:
            return

        candidates = generate_alerts(comparison, settings=alert_settings)
        print_alert_candidates(candidates, limit=limit)


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
