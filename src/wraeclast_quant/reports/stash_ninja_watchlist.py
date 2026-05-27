from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.stash_ninja_watchlist_payload import (
    STASH_NINJA_WATCHLIST_SCHEMA_VERSION,
    build_stash_ninja_watchlist,
)
from wraeclast_quant.reports.stash_ninja_watchlist_rendering import (
    render_stash_ninja_watchlist_markdown,
)

DEFAULT_STASH_NINJA_WATCHLIST_PATH = Path("data/processed/exile_ui_stash_ninja_watchlist.json")


def write_stash_ninja_watchlist(payload: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_stash_ninja_watchlist_markdown(payload: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_stash_ninja_watchlist_markdown(payload), encoding="utf-8")
    return output_path


__all__ = [
    "DEFAULT_STASH_NINJA_WATCHLIST_PATH",
    "STASH_NINJA_WATCHLIST_SCHEMA_VERSION",
    "build_stash_ninja_watchlist",
    "render_stash_ninja_watchlist_markdown",
    "write_stash_ninja_watchlist",
    "write_stash_ninja_watchlist_markdown",
]
