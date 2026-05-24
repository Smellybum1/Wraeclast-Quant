from __future__ import annotations

from pathlib import Path


def daily_args(
    *,
    sample_data: bool = False,
    input_path: Path | None = None,
    database_path: Path,
    brief_path: Path | None = None,
    intel_path: Path | None = None,
    site_dir: Path | None = None,
    big_delta: int | None = None,
) -> list[str]:
    args = ["daily"]
    if sample_data:
        args.append("--sample-data")
    if input_path is not None:
        args.extend(["--input-path", str(input_path)])
    args.extend(["--database-path", str(database_path)])
    if brief_path is not None:
        args.extend(["--brief-path", str(brief_path)])
    if intel_path is not None:
        args.extend(["--intel-path", str(intel_path)])
    if site_dir is not None:
        args.extend(["--site-dir", str(site_dir)])
    if big_delta is not None:
        args.extend(["--big-delta", str(big_delta)])
    return args


def schedule_helper_args(
    *,
    sample_data: bool = False,
    input_path: Path | None = None,
    time: str | None = None,
) -> list[str]:
    args = ["schedule-helper"]
    if sample_data:
        args.append("--sample-data")
    if input_path is not None:
        args.extend(["--input-path", str(input_path)])
    if time is not None:
        args.extend(["--time", time])
    return args


__all__ = ["daily_args", "schedule_helper_args"]
