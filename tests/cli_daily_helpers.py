from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_snapshot_helpers import save_single_opportunity_run


def previous_stormglass_database(tmp_path: Path) -> Path:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    save_single_opportunity_run(
        repository,
        "Stormglass Catalyst",
        50.0,
        "HOLD / SELL SELECTIVELY",
    )
    return database_path


def small_mover_daily_setup(tmp_path: Path) -> tuple[Path, Path]:
    database_path = tmp_path / "snapshots.db"
    input_path = tmp_path / "items.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "name": "Small Mover",
                    "signals": {
                        "demand_momentum": 100,
                        "build_dependency_score": 0,
                        "price_discount_score": 0,
                        "liquidity_score": 66.6667,
                        "historical_spike_score": 0,
                        "patch_relevance_score": 0,
                        "manipulation_risk": 0,
                        "stale_data_penalty": 0,
                    },
                }
            ]
        ),
        encoding="utf-8",
    )
    repository = SnapshotRepository(database_path)
    save_single_opportunity_run(repository, "Small Mover", 20.0, "AVOID")
    return database_path, input_path


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


__all__ = ["daily_args", "previous_stormglass_database", "small_mover_daily_setup"]
