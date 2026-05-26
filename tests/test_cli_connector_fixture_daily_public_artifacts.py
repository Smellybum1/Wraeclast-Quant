import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_connector_fixture_command_helpers import (
    connector_fixture_daily_args as _connector_fixture_daily_args,
)


runner = CliRunner()


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
