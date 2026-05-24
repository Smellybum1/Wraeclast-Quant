from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.importers.manual import ManualImportError, load_manual_items
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.workflows.daily_pipeline import create_alert_settings


def daily_opportunities(sample_data: bool, input_path: Path | None):
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


def daily_alert_settings(
    watch_threshold: float,
    buy_threshold: float,
    big_delta: float,
) -> AlertRuleSettings:
    try:
        return create_alert_settings(watch_threshold, buy_threshold, big_delta)
    except ValueError as error:
        raise typer.BadParameter(str(error)) from error


__all__ = [
    "daily_alert_settings",
    "daily_opportunities",
]
