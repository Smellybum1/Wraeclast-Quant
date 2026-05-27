from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.stash_ninja_watchlist import (
    STASH_NINJA_WATCHLIST_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class StashNinjaWatchlistHealthResult:
    path: Path
    valid: bool
    errors: list[str]
    schema_version: str
    latest_run_id: int | None
    item_count: int | None


def check_stash_ninja_watchlist_health(
    path: Path,
) -> StashNinjaWatchlistHealthResult | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return StashNinjaWatchlistHealthResult(
            path=path,
            valid=False,
            errors=[f"invalid JSON: {error}"],
            schema_version="",
            latest_run_id=None,
            item_count=None,
        )
    if not isinstance(payload, dict):
        return StashNinjaWatchlistHealthResult(
            path=path,
            valid=False,
            errors=["payload must be an object"],
            schema_version="",
            latest_run_id=None,
            item_count=None,
        )
    return _health_from_payload(path, payload)


def _health_from_payload(path: Path, payload: dict[str, Any]) -> StashNinjaWatchlistHealthResult:
    errors: list[str] = []
    schema_version = str(payload.get("schema_version", ""))
    if schema_version != STASH_NINJA_WATCHLIST_SCHEMA_VERSION:
        errors.append(
            "schema_version must be "
            f"{STASH_NINJA_WATCHLIST_SCHEMA_VERSION}, got {schema_version or '<missing>'}"
        )

    latest_run = payload.get("latest_run")
    latest_run_id = _latest_run_id(latest_run, errors)

    items = payload.get("items")
    item_count = _item_count(items, errors)

    safety = payload.get("safety")
    if not isinstance(safety, dict) or safety.get("derived_only") is not True:
        errors.append("safety.derived_only must be true")
    if not isinstance(safety, dict) or safety.get("no_exile_ui_writes") is not True:
        errors.append("safety.no_exile_ui_writes must be true")
    if not isinstance(safety, dict) or safety.get("no_game_client_interaction") is not True:
        errors.append("safety.no_game_client_interaction must be true")

    return StashNinjaWatchlistHealthResult(
        path=path,
        valid=not errors,
        errors=errors,
        schema_version=schema_version,
        latest_run_id=latest_run_id,
        item_count=item_count,
    )


def _latest_run_id(latest_run: object, errors: list[str]) -> int | None:
    if not isinstance(latest_run, dict):
        errors.append("latest_run must be an object")
        return None
    run_id = latest_run.get("id")
    if not isinstance(run_id, int):
        errors.append("latest_run.id must be an integer")
        return None
    return run_id


def _item_count(items: object, errors: list[str]) -> int | None:
    if not isinstance(items, list):
        errors.append("items must be a list")
        return None
    return len(items)


__all__ = ["StashNinjaWatchlistHealthResult", "check_stash_ninja_watchlist_health"]
