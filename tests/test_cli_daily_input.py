import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_daily_command_helpers import daily_args as _daily_args
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


runner = CliRunner()


def test_daily_input_path_writes_artifacts(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _daily_args(
            input_path=input_path,
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
    assert "Daily run #1 complete." in result.output
    assert "Manual Daily Catalyst" in intel_path.read_text(encoding="utf-8")


def test_daily_input_path_creates_one_manual_import_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _daily_args(input_path=input_path, database_path=database_path),
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"


def test_daily_input_path_public_intel_latest_run_matches_created_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _daily_args(input_path=input_path, database_path=database_path, intel_path=intel_path),
    )

    latest = SnapshotRepository(database_path).latest_run()
    payload = json.loads(intel_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert latest is not None
    assert payload["latest_run"]["id"] == latest.id


def test_daily_input_path_static_site_includes_imported_item(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    site_dir = tmp_path / "site"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _daily_args(input_path=input_path, database_path=database_path, site_dir=site_dir),
    )

    assert result.exit_code == 0
    assert "Manual Daily Catalyst" in (site_dir / "index.html").read_text(encoding="utf-8")
