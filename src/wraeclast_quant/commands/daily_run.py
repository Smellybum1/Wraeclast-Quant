from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.daily_run_rendering import print_daily_result
from wraeclast_quant.importers.manual import ManualImportError, load_manual_items
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.workflows.daily_pipeline import create_alert_settings, run_daily_pipeline


def register(app: typer.Typer) -> None:
    @app.command()
    def daily(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        input_path: Path | None = typer.Option(None, "--input-path", help="Local JSON or CSV signal file."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        brief_path: Path = typer.Option(Path("data/processed/market_brief.md"), "--brief-path"),
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
        watch_threshold: float = typer.Option(55.0, "--watch-threshold", min=0, max=100),
        buy_threshold: float = typer.Option(75.0, "--buy-threshold", min=0, max=100),
        big_delta: float = typer.Option(10.0, "--big-delta", min=0, max=100),
    ) -> None:
        alert_settings = _alert_settings(watch_threshold, buy_threshold, big_delta)
        source_mode, opportunities = _daily_opportunities(sample_data, input_path)
        result = run_daily_pipeline(
            opportunities=opportunities,
            source_mode=source_mode,
            database_path=database_path,
            resources_path=resources_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
            limit=limit,
            alert_settings=alert_settings,
        )
        print_daily_result(result, database_path=database_path, limit=limit)


def _daily_opportunities(sample_data: bool, input_path: Path | None):
    if sample_data and input_path is not None:
        raise typer.BadParameter("Use either --sample-data or --input-path, not both.")
    if sample_data:
        return "sample-data", rank_opportunities(SAMPLE_ITEMS)
    if input_path is not None:
        try:
            return "manual-import", rank_opportunities(load_manual_items(input_path))
        except ManualImportError as error:
            raise typer.BadParameter(str(error)) from error
    raise typer.BadParameter("Use --sample-data or --input-path for daily runs.")


def _alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    try:
        return create_alert_settings(watch_threshold, buy_threshold, big_delta)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error
