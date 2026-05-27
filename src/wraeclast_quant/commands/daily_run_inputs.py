from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.importers.manual import ManualImportError, load_manual_items
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.workflows.daily_pipeline import RunProvenanceInput, create_alert_settings


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


def daily_manual_import_provenance(
    input_path: Path | None,
    *,
    item_count: int,
) -> RunProvenanceInput | None:
    if input_path is None:
        return None
    return RunProvenanceInput(
        source_kind="manual-import",
        resource_name="Local manual import",
        connector_id="manual-import",
        access_method="local-file",
        metadata={
            "input_file_name": input_path.name,
            "input_file_suffix": input_path.suffix.lower(),
            "input_path_kind": "absolute" if input_path.is_absolute() else "relative",
            "input_path": "<absolute path omitted>" if input_path.is_absolute() else str(input_path),
            "manual_import_item_count": item_count,
            "live_collection": False,
            "source_approval": False,
        },
    )


__all__ = [
    "daily_alert_settings",
    "daily_manual_import_provenance",
    "daily_opportunities",
]
