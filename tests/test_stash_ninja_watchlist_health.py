import json
from pathlib import Path

from wraeclast_quant.reports.stash_ninja_watchlist_health import (
    check_stash_ninja_watchlist_health,
)


def _valid_payload() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "latest_run": {"id": 7},
        "items": [{"item_name": "Exalted Orb"}],
        "safety": {
            "derived_only": True,
            "no_exile_ui_writes": True,
            "no_game_client_interaction": True,
        },
    }


def test_stash_ninja_watchlist_health_returns_none_for_missing_file(tmp_path: Path) -> None:
    result = check_stash_ninja_watchlist_health(tmp_path / "missing.json")

    assert result is None


def test_stash_ninja_watchlist_health_accepts_minimal_valid_payload(tmp_path: Path) -> None:
    path = tmp_path / "stash_ninja.json"
    path.write_text(json.dumps(_valid_payload()), encoding="utf-8")

    result = check_stash_ninja_watchlist_health(path)

    assert result is not None
    assert result.valid is True
    assert result.errors == []
    assert result.schema_version == "1.0"
    assert result.latest_run_id == 7
    assert result.item_count == 1
    assert result.calibration_prompt_count is None


def test_stash_ninja_watchlist_health_accepts_optional_calibration_prompt_count(
    tmp_path: Path,
) -> None:
    path = tmp_path / "stash_ninja.json"
    payload = _valid_payload()
    payload["calibration_prompt_count"] = 2
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = check_stash_ninja_watchlist_health(path)

    assert result is not None
    assert result.valid is True
    assert result.errors == []
    assert result.calibration_prompt_count == 2


def test_stash_ninja_watchlist_health_reports_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "stash_ninja.json"
    path.write_text("{", encoding="utf-8")

    result = check_stash_ninja_watchlist_health(path)

    assert result is not None
    assert result.valid is False
    assert any(error.startswith("invalid JSON:") for error in result.errors)
    assert result.latest_run_id is None
    assert result.item_count is None


def test_stash_ninja_watchlist_health_reports_contract_and_safety_errors(tmp_path: Path) -> None:
    path = tmp_path / "stash_ninja.json"
    payload = _valid_payload()
    payload.update(
        {
            "schema_version": "0.9",
            "latest_run": {"id": "7"},
            "items": "not-items",
            "calibration_prompt_count": -1,
            "safety": {
                "derived_only": False,
                "no_exile_ui_writes": False,
                "no_game_client_interaction": False,
            },
        }
    )
    path.write_text(json.dumps(payload), encoding="utf-8")

    result = check_stash_ninja_watchlist_health(path)

    assert result is not None
    assert result.valid is False
    assert "schema_version must be 1.0, got 0.9" in result.errors
    assert "latest_run.id must be an integer" in result.errors
    assert "items must be a list" in result.errors
    assert "calibration_prompt_count must be a nonnegative integer when present" in result.errors
    assert "safety.derived_only must be true" in result.errors
    assert "safety.no_exile_ui_writes must be true" in result.errors
    assert "safety.no_game_client_interaction must be true" in result.errors
