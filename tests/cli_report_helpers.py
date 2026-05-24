from __future__ import annotations

from pathlib import Path


def analyze_sample_args(database_path: Path) -> list[str]:
    return ["analyze", "--sample-data", "--database-path", str(database_path)]


def report_sample_args(database_path: Path | None = None) -> list[str]:
    args = ["report", "--sample-data"]
    if database_path is not None:
        args.extend(["--database-path", str(database_path)])
    return args


def watchlist_args() -> list[str]:
    return ["watchlist"]


__all__ = ["analyze_sample_args", "report_sample_args", "watchlist_args"]
