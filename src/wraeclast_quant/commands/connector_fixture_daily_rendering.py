from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.snapshot_rendering import print_alert_candidates
from wraeclast_quant.workflows.daily_pipeline import DailyPipelineResult


def print_connector_fixture_daily_result(
    result: DailyPipelineResult | None,
    *,
    database_path: Path,
    limit: int,
) -> None:
    if result is None:
        console.print("No snapshots found.")
        return

    console.print(f"Connector fixture daily run #{result.run.id} complete.")
    console.print(f"Database: {database_path}")
    console.print(f"Market brief: {result.brief_path}")
    console.print(f"Public intel: {result.intel_path}")
    console.print(f"Dashboard: {result.site_path}")

    if result.comparison is None:
        console.print("No previous snapshot found for comparison.")
        return
    print_alert_candidates(result.alert_candidates, limit=limit)
