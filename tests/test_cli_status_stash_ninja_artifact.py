from pathlib import Path

from wraeclast_quant.commands.status_health_stash_ninja_artifact import (
    stash_ninja_details,
    stash_ninja_run_id,
    stash_ninja_status,
)
from wraeclast_quant.reports.stash_ninja_watchlist_health import (
    StashNinjaWatchlistHealthResult,
)


def _health(
    *,
    valid: bool = True,
    errors: list[str] | None = None,
    run_id: int | None = 7,
    item_count: int | None = 3,
    calibration_prompt_count: int | None = None,
) -> StashNinjaWatchlistHealthResult:
    return StashNinjaWatchlistHealthResult(
        path=Path("stash_ninja.json"),
        valid=valid,
        errors=errors or [],
        schema_version="1.0",
        latest_run_id=run_id,
        item_count=item_count,
        calibration_prompt_count=calibration_prompt_count,
    )


def test_stash_ninja_status_row_allows_missing_optional_handoff() -> None:
    path = Path("missing.json")

    assert stash_ninja_status(None) == "none"
    assert stash_ninja_run_id(None) is None
    assert stash_ninja_details(path, None, latest_run_id=7) == (
        "missing.json not found; optional: run wq stash-ninja-watchlist"
    )


def test_stash_ninja_status_row_reports_invalid_handoff() -> None:
    health = _health(valid=False, errors=["items must be a list"])

    assert stash_ninja_status(health) == "needs attention"
    assert stash_ninja_run_id(health) is None
    assert stash_ninja_details(Path("stash_ninja.json"), health, latest_run_id=7) == (
        "stash_ninja.json; invalid: items must be a list; run wq stash-ninja-watchlist"
    )


def test_stash_ninja_status_row_reports_fresh_handoff() -> None:
    health = _health()

    assert stash_ninja_status(health) == "ok"
    assert stash_ninja_run_id(health) == 7
    assert stash_ninja_details(Path("stash_ninja.json"), health, latest_run_id=7) == (
        "stash_ninja.json; schema 1.0; latest run #7; 3 items; "
        "manual-only companion handoff"
    )


def test_stash_ninja_status_row_reports_calibration_prompt_count() -> None:
    health = _health(calibration_prompt_count=2)

    assert stash_ninja_details(Path("stash_ninja.json"), health, latest_run_id=7) == (
        "stash_ninja.json; schema 1.0; latest run #7; 3 items; "
        "2 calibration prompt(s); manual-only companion handoff"
    )


def test_stash_ninja_status_row_reports_stale_handoff() -> None:
    health = _health(run_id=3)

    assert stash_ninja_details(Path("stash_ninja.json"), health, latest_run_id=7) == (
        "stash_ninja.json; schema 1.0; latest run #3; 3 items; "
        "manual-only companion handoff; stale; latest database run #7, "
        "handoff run #3; run wq stash-ninja-watchlist"
    )
