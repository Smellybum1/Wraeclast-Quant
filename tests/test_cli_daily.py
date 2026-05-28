from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_daily_command_helpers import daily_args as _daily_args
from cli_daily_fixture_helpers import previous_stormglass_database as _previous_stormglass_database


runner = CliRunner()


def test_daily_sample_data_writes_artifacts(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _daily_args(
            sample_data=True,
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
    assert str(brief_path) in result.output
    assert str(intel_path) in result.output
    assert "wq run-provenance" not in result.output


def test_daily_creates_exactly_one_analysis_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _daily_args(
            sample_data=True,
            database_path=database_path,
            brief_path=tmp_path / "market_brief.md",
            intel_path=tmp_path / "public_intel.json",
            site_dir=tmp_path / "site",
        ),
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert len(runs) == 1


def test_daily_brief_includes_snapshot_changes_with_previous_run(tmp_path: Path) -> None:
    database_path = _previous_stormglass_database(tmp_path)
    brief_path = tmp_path / "market_brief.md"

    result = runner.invoke(
        app,
        _daily_args(sample_data=True, database_path=database_path, brief_path=brief_path),
    )

    assert result.exit_code == 0
    assert "## Snapshot Changes" in brief_path.read_text(encoding="utf-8")
