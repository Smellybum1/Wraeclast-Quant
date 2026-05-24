from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_domain_helpers import manual_item
from cli_snapshot_helpers import save_single_opportunity_run


def write_connector_fixture(tmp_path: Path, payload: dict[str, object]) -> Path:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(payload), encoding="utf-8")
    return fixture_path


def write_invalid_connector_fixture(tmp_path: Path) -> Path:
    return write_connector_fixture(
        tmp_path,
        {"source_name": "Example Approved API", "generated_at": "now"},
    )


def write_basic_connector_fixture(tmp_path: Path) -> Path:
    return write_connector_fixture(
        tmp_path,
        {
            "source_name": "Approved API",
            "generated_at": "2026-05-23T00:00:00+00:00",
            "items": [{"name": "Stormglass Catalyst"}],
        },
    )


def connector_fixture_daily_tuned_setup(tmp_path: Path) -> tuple[Path, Path]:
    database_path = tmp_path / "snapshots.db"
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "source_name": "Example Approved API",
                "generated_at": "2026-05-23T00:00:00+00:00",
                "items": [
                    {
                        "name": "Stormglass Catalyst",
                        "signals": manual_item("Stormglass Catalyst")["signals"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    repository = SnapshotRepository(database_path)
    save_single_opportunity_run(
        repository,
        "Stormglass Catalyst",
        60.0,
        "WATCH",
        source_mode="connector-fixture",
    )
    return database_path, fixture_path


__all__ = [
    "connector_fixture_daily_tuned_setup",
    "write_basic_connector_fixture",
    "write_connector_fixture",
    "write_invalid_connector_fixture",
]
