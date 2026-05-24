import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_connector_fixture_command_helpers import connector_dry_run_args as _connector_dry_run_args
from cli_connector_fixture_command_helpers import (
    connector_fixture_export_args as _connector_fixture_export_args,
)
from cli_connector_fixture_command_helpers import (
    connector_fixture_daily_args as _connector_fixture_daily_args,
)
from cli_connector_fixture_command_helpers import (
    connector_fixture_run_args as _connector_fixture_run_args,
)
from cli_connector_fixture_data_helpers import (
    connector_fixture_daily_tuned_setup as _connector_fixture_daily_tuned_setup,
)
from cli_connector_fixture_data_helpers import (
    write_basic_connector_fixture as _write_basic_connector_fixture,
)
from cli_connector_fixture_data_helpers import (
    write_invalid_connector_fixture as _write_invalid_connector_fixture,
)
from cli_connector_helpers import write_connector_resources as _write_connector_resources
from cli_connector_helpers import write_connector_review as _write_connector_review


runner = CliRunner()


def test_connector_fixture_run_prints_rows_and_count() -> None:
    result = runner.invoke(
        app,
        _connector_fixture_run_args(),
    )

    assert result.exit_code == 0
    assert "Connector Fixture Rows" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Fixture rows: 2" in result.output
    assert "Fetch plan cache path" in result.output
    assert "No network requests were made" in result.output


def test_connector_fixture_run_refuses_incomplete_review() -> None:
    result = runner.invoke(
        app,
        _connector_fixture_run_args(
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
        ),
    )

    assert result.exit_code != 0
    assert "Connector Fixture Run" in result.output
    assert "Source terms must be reviewed." in result.output


def test_connector_fixture_run_invalid_fixture_exits_nonzero(tmp_path: Path) -> None:
    fixture_path = _write_invalid_connector_fixture(tmp_path)

    result = runner.invoke(
        app,
        _connector_fixture_run_args(fixture_path=fixture_path),
    )

    assert result.exit_code != 0
    assert "Invalid connector fixture" in result.output


def test_connector_dry_run_prints_connector_class_rows_and_cache_path() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(),
    )

    assert result.exit_code == 0
    assert "Connector Dry Run" in result.output
    assert "FixtureSourceConnector" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Future cache path" in result.output
    assert "No network requests were made" in result.output


def test_connector_dry_run_prints_poe_ninja_currency_connector() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path="examples/reviews/poe_ninja_poe2_currency_connector_review.json",
            fixture_path="examples/poe_ninja_poe2_currency_fixture.json",
        ),
    )

    assert result.exit_code == 0
    assert "PoeNinjaCurrencyConnector" in result.output
    assert "poe-ninja-poe2-currency" in result.output
    assert "Exalted Orb" in result.output
    assert "No network requests were made" in result.output


def test_connector_dry_run_refuses_incomplete_review() -> None:
    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
        ),
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output


def test_connector_dry_run_is_read_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    fixture_path = _write_basic_connector_fixture(tmp_path)
    resources_path = _write_connector_resources(
        tmp_path,
        "\n## Fixture Sources\n- name: Approved API\n  type: official\n  url: https://example.test/api\n  allowed_use: api\n",
    )
    review_path = _write_connector_review(tmp_path)

    result = runner.invoke(
        app,
        _connector_dry_run_args(
            review_path=review_path,
            fixture_path=fixture_path,
            resources_path=resources_path,
        ),
    )

    assert result.exit_code == 0
    assert not Path("data/raw/cache").exists()
    assert not Path("data/wraeclast_quant.db").exists()


def test_connector_fixture_export_writes_manual_import_json(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        _connector_fixture_export_args(output_path=output_path),
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Connector Fixture Export" in result.output
    assert "2" in result.output
    assert str(output_path) in result.output
    assert payload["items"][0]["name"] == "Stormglass Catalyst"
    assert "signals" in payload["items"][0]


def test_connector_fixture_export_rejects_fixture_without_signals(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        _connector_fixture_export_args(
            output_path=output_path,
            fixture_path="examples/connector_fixture_api_example.json",
        ),
    )

    assert result.exit_code != 0
    assert "requires normalized signals" in result.output
    assert not output_path.exists()


def test_connector_fixture_export_refuses_incomplete_review(tmp_path: Path) -> None:
    output_path = tmp_path / "connector_manual_import.json"

    result = runner.invoke(
        app,
        _connector_fixture_export_args(
            output_path=output_path,
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
        ),
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output
    assert not output_path.exists()


def test_connector_fixture_daily_writes_artifacts(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            database_path=database_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
        ),
    )

    assert result.exit_code == 0
    assert brief_path.exists()
    assert intel_path.exists()
    assert (site_dir / "index.html").exists()
    assert "Connector fixture daily run #1 complete." in result.output
    assert str(brief_path) in result.output
    assert str(intel_path) in result.output


def test_connector_fixture_daily_creates_one_connector_fixture_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(database_path=database_path),
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert len(runs) == 1
    assert runs[0].source_mode == "connector-fixture"


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


def test_connector_fixture_daily_public_intel_latest_run_matches_created_run(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(database_path=database_path, intel_path=intel_path),
    )

    latest = SnapshotRepository(database_path).latest_run()
    payload = json.loads(intel_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert latest is not None
    assert payload["latest_run"]["id"] == latest.id
    assert payload["latest_run"]["source_mode"] == "connector-fixture"


def test_connector_fixture_daily_static_site_includes_fixture_items(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(database_path=database_path, site_dir=site_dir),
    )

    assert result.exit_code == 0
    site_text = (site_dir / "index.html").read_text(encoding="utf-8")
    assert "Stormglass Catalyst" in site_text
    assert "Ashen Rune Core" in site_text


def test_connector_fixture_daily_rejects_fixture_without_signals(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            fixture_path="examples/connector_fixture_api_example.json",
            database_path=database_path,
        ),
    )

    assert result.exit_code != 0
    assert "requires normalized signals" in result.output
    assert not database_path.exists()


def test_connector_fixture_daily_refuses_incomplete_review(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            review_path="examples/poe_ninja_poe2_currency_connector_review.json",
            database_path=database_path,
        ),
    )

    assert result.exit_code != 0
    assert "Source terms must be reviewed." in result.output
    assert not database_path.exists()


def test_connector_fixture_daily_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path, fixture_path = _connector_fixture_daily_tuned_setup(tmp_path)

    result = runner.invoke(
        app,
        _connector_fixture_daily_args(
            fixture_path=fixture_path,
            database_path=database_path,
            big_delta=20,
        ),
    )

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output
