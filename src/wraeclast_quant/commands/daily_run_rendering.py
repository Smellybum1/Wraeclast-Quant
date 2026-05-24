from __future__ import annotations

from pathlib import Path

from rich.console import Console

from wraeclast_quant.commands.snapshot_rendering import print_alert_candidates
from wraeclast_quant.workflows.daily_pipeline import DailyPipelineResult

console = Console(width=260)


def print_daily_result(
    result: DailyPipelineResult | None,
    *,
    database_path: Path,
    limit: int,
) -> None:
    if result is None:
        console.print("No snapshots found.")
        return

    console.print(f"Daily run #{result.run.id} complete.")
    console.print(f"Database: {database_path}")
    console.print(f"Market brief: {result.brief_path}")
    console.print(f"Public intel: {result.intel_path}")
    console.print(f"Dashboard: {result.site_path}")

    if result.comparison is None:
        console.print("No previous snapshot found for comparison.")
        return
    print_alert_candidates(result.alert_candidates, limit=limit)
