from __future__ import annotations

import json
from pathlib import Path


def write_connector_fixture(tmp_path: Path, payload: dict[str, object]) -> Path:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(payload), encoding="utf-8")
    return fixture_path


def missing_items_fixture_payload() -> dict[str, object]:
    return {"source_name": "Example Approved API", "generated_at": "now"}


def unnamed_item_fixture_payload() -> dict[str, object]:
    return {
        "source_name": "Example Approved API",
        "generated_at": "now",
        "items": [{"category": "currency"}],
    }


def invalid_signals_fixture_payload() -> dict[str, object]:
    return {
        "source_name": "Example Approved API",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "items": [
            {
                "name": "Stormglass Catalyst",
                "signals": {
                    "demand_momentum": 101,
                    "build_dependency_score": 82,
                    "price_discount_score": 76,
                    "liquidity_score": 70,
                    "historical_spike_score": 68,
                    "patch_relevance_score": 74,
                    "manipulation_risk": 18,
                    "stale_data_penalty": 8,
                },
            }
        ],
    }


def minimal_fixture_payload() -> dict[str, object]:
    return {
        "source_name": "Approved API",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "items": [{"name": "Stormglass Catalyst"}],
    }


__all__ = [
    "invalid_signals_fixture_payload",
    "minimal_fixture_payload",
    "missing_items_fixture_payload",
    "unnamed_item_fixture_payload",
    "write_connector_fixture",
]
