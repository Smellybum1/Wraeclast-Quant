from __future__ import annotations

from pathlib import Path


def compare_args(database_path: Path) -> list[str]:
    return ["compare", "--database-path", str(database_path)]


def alerts_args(
    database_path: Path,
    *,
    watch_threshold: int | None = None,
    buy_threshold: int | None = None,
    big_delta: int | None = None,
) -> list[str]:
    args = ["alerts", "--database-path", str(database_path)]
    if watch_threshold is not None:
        args.extend(["--watch-threshold", str(watch_threshold)])
    if buy_threshold is not None:
        args.extend(["--buy-threshold", str(buy_threshold)])
    if big_delta is not None:
        args.extend(["--big-delta", str(big_delta)])
    return args


__all__ = ["alerts_args", "compare_args"]
