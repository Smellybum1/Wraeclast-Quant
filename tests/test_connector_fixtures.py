from pathlib import Path

import pytest

from wraeclast_quant.config.connector_fixtures import load_connector_fixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError

from connector_policy_helpers import invalid_signals_fixture_payload as _invalid_signals_fixture_payload
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
