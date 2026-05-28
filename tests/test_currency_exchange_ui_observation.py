import json
from pathlib import Path

import pytest

from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation import (
    currency_exchange_ui_observation_capture_review_flags,
    currency_exchange_ui_observation_manual_import_payload,
    currency_exchange_ui_observation_review_flags,
    currency_exchange_ui_observation_review_notes,
    load_currency_exchange_ui_observation,
    ratio_to_float,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.importers.manual import load_manual_items


def write_ui_observation(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "league": "Standard",
                "observed_at": "2026-05-27T17:00:00+00:00",
                "observations": [
                    {
                        "want_currency": "Chaos Orb",
                        "have_currency": "Divine Orb",
                        "market_ratio": "30:1",
                        "stock_rows": [
                            {"ratio": "30:1", "stock": 18150},
                            {"ratio": "25:1", "stock": 182850},
                            {"ratio": "23.71:1", "stock": 735},
                            {"ratio": "23:1", "stock": 2300},
                            {"ratio": "22:1", "stock": 4400},
                            {"ratio": "22:1", "stock": 214257, "comparator": "less_than"},
                        ],
                    },
                    {
                        "want_currency": "Divine Orb",
                        "have_currency": "Regal Orb",
                        "market_ratio": {"want": 1, "have": 1},
                        "no_stock": True,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def test_ratio_to_float_accepts_strings_and_objects() -> None:
    assert ratio_to_float("30:1") == 30.0
    assert ratio_to_float({"want": 1, "have": 35.71}) == 1 / 35.71


def test_ui_observation_exports_manual_import_items(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    write_ui_observation(input_path)

    snapshot = load_currency_exchange_ui_observation(input_path)
    payload = currency_exchange_ui_observation_manual_import_payload(snapshot)

    assert [item["name"] for item in payload["items"]] == [
        "Chaos Orb / Divine Orb (Standard UI)",
        "Divine Orb / Regal Orb (Standard UI)",
    ]
    assert payload["items"][0]["signals"]["liquidity_score"] == 100.0
    assert payload["items"][1]["signals"]["liquidity_score"] == 0.0
    assert payload["items"][1]["signals"]["stale_data_penalty"] == 25.0


def test_ui_observation_output_is_manual_import_compatible(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    output_path = tmp_path / "manual_import.json"
    write_ui_observation(input_path)
    snapshot = load_currency_exchange_ui_observation(input_path)
    output_path.write_text(
        json.dumps(currency_exchange_ui_observation_manual_import_payload(snapshot)),
        encoding="utf-8",
    )

    items = load_manual_items(output_path)

    assert len(items) == 2
    assert items[0]["name"] == "Chaos Orb / Divine Orb (Standard UI)"


def test_ui_observation_review_notes_summarize_visible_rows(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    write_ui_observation(input_path)
    snapshot = load_currency_exchange_ui_observation(input_path)

    notes = currency_exchange_ui_observation_review_notes(snapshot)

    assert "Currency Exchange UI Observation Review Notes" in notes
    assert "Chaos Orb / Divine Orb (Standard UI)" in notes
    assert "<22:1 stock 214,257" in notes
    assert "Divine Orb / Regal Orb (Standard UI)" in notes
    assert "No Stock" in notes
    assert "## Capture Review Flags" in notes
    assert "No Stock was transcribed" in notes
    assert "Do not record outcomes until a human review decision has been made." in notes


def test_ui_observation_review_flags_name_ratio_only_captures(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    input_path.write_text(
        json.dumps(
            {
                "league": "Standard",
                "observations": [
                    {
                        "want_currency": "Exalted Orb",
                        "have_currency": "Divine Orb",
                        "market_ratio": "650:1",
                    },
                    {
                        "want_currency": "Divine Orb",
                        "have_currency": "Chaos Orb",
                        "stock_rows": [{"ratio": "1:28", "stock": 2800}],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    snapshot = load_currency_exchange_ui_observation(input_path)

    flags = currency_exchange_ui_observation_review_flags(snapshot)

    assert any(
        "Exalted Orb / Divine Orb (Standard UI): ratio-only capture" in flag
        for flag in flags
    )
    assert any(
        "Divine Orb / Chaos Orb (Standard UI): stock-ladder rows" in flag
        for flag in flags
    )
    assert currency_exchange_ui_observation_capture_review_flags(snapshot) == flags


def test_ui_observation_review_flags_report_clean_capture(tmp_path: Path) -> None:
    input_path = tmp_path / "ui_observation.json"
    input_path.write_text(
        json.dumps(
            {
                "league": "Standard",
                "observations": [
                    {
                        "want_currency": "Chaos Orb",
                        "have_currency": "Divine Orb",
                        "market_ratio": "30:1",
                        "stock_rows": [{"ratio": "30:1", "stock": 18150}],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    snapshot = load_currency_exchange_ui_observation(input_path)

    assert currency_exchange_ui_observation_review_flags(snapshot) == [
        "- No capture review flags detected."
    ]
    assert currency_exchange_ui_observation_capture_review_flags(snapshot) == []


def test_ui_observation_rejects_empty_observations(tmp_path: Path) -> None:
    input_path = tmp_path / "empty.json"
    input_path.write_text('{"league": "Standard", "observations": []}', encoding="utf-8")

    with pytest.raises(ConnectorPolicyError, match="observations must not be empty"):
        load_currency_exchange_ui_observation(input_path)
