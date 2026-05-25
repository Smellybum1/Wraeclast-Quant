import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_connector_fixture_command_helpers import (
    connector_fixture_daily_args as _connector_fixture_daily_args,
)
from cli_connector_fixture_data_helpers import (
    connector_fixture_daily_tuned_setup as _connector_fixture_daily_tuned_setup,
)


runner = CliRunner()


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
