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


__all__ = ["previous_stormglass_database", "small_mover_daily_setup"]
