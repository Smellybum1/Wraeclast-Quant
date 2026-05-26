import json
from pathlib import Path

import pytest

from wraeclast_quant.config.connector_fixtures import export_connector_fixture_signals
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.config.connector_policy import load_connector_review
from wraeclast_quant.importers.manual import load_manual_items

from connector_policy_helpers import connector_review as _review
from connector_policy_helpers import eligible_resource as _eligible_resource
from connector_policy_helpers import example_approved_api_resources as _example_approved_api_resources


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
