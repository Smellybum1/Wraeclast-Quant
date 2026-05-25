import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_connector_fixture_command_helpers import (
    connector_fixture_daily_args as _connector_fixture_daily_args,
)


runner = CliRunner()


def test_connector_fixture_daily_stores_sanitized_run_provenance(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(database_path=database_path),
    )

    provenance = SnapshotRepository(database_path).latest_run_provenance()
    assert result.exit_code == 0
    assert provenance is not None
    assert provenance.source_kind == "connector-fixture"
    assert provenance.resource_name == "Example Approved API"
    assert provenance.connector_id == "fixture-source-connector"
    assert provenance.access_method == "api"
    assert provenance.metadata["connector_class"] == "FixtureSourceConnector"
    assert provenance.metadata["fixture_item_count"] == 2
    assert provenance.metadata["review_file"] == "connector_review_api_example.json"
    assert provenance.metadata["fixture_file"] == "connector_fixture_signals_example.json"
    assert "review_sha256" in provenance.metadata
    assert "fixture_sha256" in provenance.metadata
    serialized = json.dumps(provenance.metadata, sort_keys=True)
    assert "https://" not in serialized
    assert "demand_momentum" not in serialized
    assert str(tmp_path) not in serialized


def test_connector_fixture_daily_uses_poe_ninja_connector_provenance(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            review_path="examples/reviews/poe_ninja_poe2_currency_connector_review.json",
            fixture_path="examples/poe_ninja_poe2_currency_fixture.json",
            database_path=database_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
        ),
    )

    provenance = SnapshotRepository(database_path).latest_run_provenance()
    assert result.exit_code == 0
    assert provenance is not None
    assert provenance.connector_id == "poe-ninja-poe2-currency"
    assert provenance.metadata["connector_class"] == "PoeNinjaCurrencyConnector"
