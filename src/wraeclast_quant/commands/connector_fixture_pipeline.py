from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.connector_fixture_daily_rendering import print_connector_fixture_daily_result
from wraeclast_quant.commands.connector_fixture_daily_workflow import run_connector_fixture_daily_pipeline
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.workflows.daily_pipeline import create_alert_settings


def register(app: typer.Typer) -> None:
    @app.command("connector-fixture-daily")
    def connector_fixture_daily(
        review_path: Path = typer.Option(..., "--review-path", help="Local connector review JSON file."),
        fixture_path: Path = typer.Option(..., "--fixture-path", help="Local connector fixture JSON file."),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        brief_path: Path = typer.Option(Path("data/processed/market_brief.md"), "--brief-path"),
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
        watch_threshold: float = typer.Option(55.0, "--watch-threshold", min=0, max=100),
        buy_threshold: float = typer.Option(75.0, "--buy-threshold", min=0, max=100),
        big_delta: float = typer.Option(10.0, "--big-delta", min=0, max=100),
    ) -> None:
        try:
            alert_settings = _alert_settings(watch_threshold, buy_threshold, big_delta)
            result = run_connector_fixture_daily_pipeline(
                review_path=review_path,
                fixture_path=fixture_path,
                resources_path=resources_path,
                database_path=database_path,
                brief_path=brief_path,
                intel_path=intel_path,
                site_dir=site_dir,
                limit=limit,
                alert_settings=alert_settings,
            )
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_connector_fixture_daily_result(result, database_path=database_path, limit=limit)


def _alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    try:
        return create_alert_settings(watch_threshold, buy_threshold, big_delta)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error
