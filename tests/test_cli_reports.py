from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_daily_fixture_helpers import previous_stormglass_database as _previous_stormglass_database
from cli_report_helpers import report_sample_args as _report_sample_args
from cli_report_helpers import watchlist_args as _watchlist_args


runner = CliRunner()


def test_report_sample_data(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("data/processed").mkdir(parents=True)

    result = runner.invoke(app, _report_sample_args())

    assert result.exit_code == 0
    assert Path("data/processed/market_brief.md").exists()


def test_watchlist() -> None:
    result = runner.invoke(app, _watchlist_args())

    assert result.exit_code == 0
    assert "Watchlist" in result.output


def test_report_sample_data_records_artifact(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _report_sample_args(database_path),
    )

    assert result.exit_code == 0
    assert Path("data/processed/market_brief.md").exists()
    assert database_path.exists()
    assert "Recorded report artifact" in result.output


def test_report_sample_data_includes_snapshot_changes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    database_path = _previous_stormglass_database(tmp_path)

    result = runner.invoke(
        app,
        _report_sample_args(database_path),
    )

    report = Path("data/processed/market_brief.md").read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "## Snapshot Changes" in report
