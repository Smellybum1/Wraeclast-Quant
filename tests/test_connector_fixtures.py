import json
from pathlib import Path

import pytest

from wraeclast_quant.config.connector_fixtures import (
    export_connector_fixture_signals,
    load_connector_fixture,
    run_connector_fixture,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.config.connector_policy import load_connector_review
from wraeclast_quant.importers.manual import load_manual_items

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import example_approved_api_resources as _example_approved_api_resources
from connector_policy_helpers import invalid_signals_fixture_payload as _invalid_signals_fixture_payload
from connector_policy_helpers import minimal_fixture_payload as _minimal_fixture_payload
from connector_policy_helpers import missing_items_fixture_payload as _missing_items_fixture_payload
from connector_policy_helpers import unnamed_item_fixture_payload as _unnamed_item_fixture_payload
from connector_policy_helpers import write_connector_fixture as _write_connector_fixture


def test_connector_fixture_loads_and_normalizes_rows() -> None:
    fixture = load_connector_fixture("examples/connector_fixture_api_example.json")

    assert fixture.source_name == "Example Approved API"
    assert len(fixture.items) == 2
    assert fixture.items[0].name == "Stormglass Catalyst"
    assert fixture.items[0].category == "currency"


def test_connector_fixture_loads_optional_normalized_signals() -> None:
    fixture = load_connector_fixture("examples/connector_fixture_signals_example.json")

    assert fixture.items[0].signals is not None
    assert fixture.items[0].signals.demand_momentum == 88


def test_connector_fixture_missing_items_fails_clearly(tmp_path: Path) -> None:
    fixture_path = _write_connector_fixture(tmp_path, _missing_items_fixture_payload())

    with pytest.raises(ConnectorPolicyError, match="Invalid connector fixture"):
        load_connector_fixture(fixture_path)


def test_connector_fixture_item_without_name_fails_clearly(tmp_path: Path) -> None:
    fixture_path = _write_connector_fixture(tmp_path, _unnamed_item_fixture_payload())

    with pytest.raises(ConnectorPolicyError, match="Invalid connector fixture"):
        load_connector_fixture(fixture_path)


def test_connector_fixture_invalid_signals_fail_clearly(tmp_path: Path) -> None:
    fixture_path = _write_connector_fixture(tmp_path, _invalid_signals_fixture_payload())

    with pytest.raises(ConnectorPolicyError, match="Invalid connector fixture"):
        load_connector_fixture(fixture_path)


def test_connector_fixture_runner_refuses_failed_review() -> None:
    result = run_connector_fixture(
        _review(source_terms_reviewed=False),
        [_eligible_resource()],
        "examples/connector_fixture_api_example.json",
    )

    assert result.ready is False
    assert result.fixture is None
    assert "Source terms must be reviewed." in result.blockers


def test_connector_fixture_runner_accepts_approved_example_review() -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    result = run_connector_fixture(
        review,
        _example_approved_api_resources(),
        "examples/connector_fixture_api_example.json",
    )

    assert result.ready is True
    assert result.fixture is not None
    assert result.fetch_plan is not None
    assert len(result.rows) == 2
    assert result.fetch_plan.cache_path.name.endswith(".cache")


def test_connector_fixture_signal_export_writes_manual_import_json(tmp_path: Path) -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    output_path = tmp_path / "manual_import.json"

    export = export_connector_fixture_signals(
        review,
        _example_approved_api_resources(),
        "examples/connector_fixture_signals_example.json",
        output_path,
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    imported = load_manual_items(output_path)

    assert export.item_count == 2
    assert payload["items"][0]["name"] == "Stormglass Catalyst"
    assert "signals" in payload["items"][0]
    assert imported[0]["name"] == "Stormglass Catalyst"


def test_connector_fixture_signal_export_requires_signals(tmp_path: Path) -> None:
    review = load_connector_review("examples/connector_review_api_example.json")
    output_path = tmp_path / "manual_import.json"

    with pytest.raises(ConnectorPolicyError, match="requires normalized signals"):
        export_connector_fixture_signals(
            review,
            _example_approved_api_resources(),
            "examples/connector_fixture_api_example.json",
            output_path,
        )

    assert not output_path.exists()


def test_connector_fixture_signal_export_refuses_failed_review(tmp_path: Path) -> None:
    output_path = tmp_path / "manual_import.json"

    with pytest.raises(ConnectorPolicyError, match="Source terms must be reviewed"):
        export_connector_fixture_signals(
            _review(source_terms_reviewed=False),
            [_eligible_resource()],
            "examples/connector_fixture_signals_example.json",
            output_path,
        )

    assert not output_path.exists()


def test_connector_fixture_runner_does_not_write_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = _write_connector_fixture(tmp_path, _minimal_fixture_payload())
    result = run_connector_fixture(
        _review(),
        [_eligible_resource()],
        fixture_path,
    )

    assert result.ready is True
    assert not Path("data/raw/cache").exists()
