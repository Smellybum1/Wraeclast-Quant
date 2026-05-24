from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.connector_fixture_daily_inputs import (
    connector_fixture_daily_provenance,
    load_connector_fixture_daily_input,
)
from wraeclast_quant.intelligence.alerts import AlertRuleSettings
from wraeclast_quant.workflows.daily_pipeline import DailyPipelineResult, run_daily_pipeline


def run_connector_fixture_daily_pipeline(
    *,
    review_path: Path,
    fixture_path: Path,
    resources_path: Path,
    database_path: Path,
    brief_path: Path,
    intel_path: Path,
    site_dir: Path,
    limit: int,
    alert_settings: AlertRuleSettings,
) -> DailyPipelineResult | None:
    daily_input = load_connector_fixture_daily_input(
        review_path=review_path,
        fixture_path=fixture_path,
        resources_path=resources_path,
    )
    return run_daily_pipeline(
        opportunities=daily_input.opportunities,
        source_mode="connector-fixture",
        database_path=database_path,
        resources_path=resources_path,
        brief_path=brief_path,
        intel_path=intel_path,
        site_dir=site_dir,
        limit=limit,
        alert_settings=alert_settings,
        provenance=connector_fixture_daily_provenance(
            daily_input=daily_input,
            review_path=review_path,
            fixture_path=fixture_path,
        ),
    )
