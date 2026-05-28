from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.stash_ninja_watchlist_health import (
    StashNinjaWatchlistHealthResult,
)


def stash_ninja_status(health: StashNinjaWatchlistHealthResult | None) -> str:
    if health is None:
        return "none"
    if not health.valid:
        return "needs attention"
    return "ok"


def stash_ninja_run_id(health: StashNinjaWatchlistHealthResult | None) -> int | None:
    if health is None or not health.valid:
        return None
    return health.latest_run_id


def stash_ninja_details(
    path: Path,
    health: StashNinjaWatchlistHealthResult | None,
    latest_run_id: int | None,
) -> str:
    if health is None:
        return f"{path} not found; optional: run wq stash-ninja-watchlist"
    if not health.valid:
        return f"{path}; invalid: {'; '.join(health.errors)}; run wq stash-ninja-watchlist"
    details = (
        f"{path}; schema {health.schema_version}; latest run #{health.latest_run_id}; "
        f"{health.item_count} items"
    )
    if health.calibration_prompt_count:
        details = f"{details}; {health.calibration_prompt_count} calibration prompt(s)"
    details = f"{details}; manual-only companion handoff"
    if latest_run_id is not None and health.latest_run_id != latest_run_id:
        return (
            f"{details}; stale; latest database run #{latest_run_id}, "
            f"handoff run #{health.latest_run_id}; run wq stash-ninja-watchlist"
        )
    return details


__all__ = ["stash_ninja_details", "stash_ninja_run_id", "stash_ninja_status"]
