import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_daily_command_helpers import daily_args as _daily_args


runner = CliRunner()


def test_daily_public_intel_latest_run_matches_daily_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _daily_args(sample_data=True, database_path=database_path, intel_path=intel_path),
    )

    latest = SnapshotRepository(database_path).latest_run()
    payload = json.loads(intel_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert latest is not None
    assert payload["latest_run"]["id"] == latest.id


def test_daily_site_includes_title(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _daily_args(sample_data=True, database_path=database_path, site_dir=site_dir),
    )

    assert result.exit_code == 0
    assert "Wraeclast Quant" in (site_dir / "index.html").read_text(encoding="utf-8")
