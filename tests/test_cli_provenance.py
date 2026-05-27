from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_provenance_command_helpers import run_provenance_args as _run_provenance_args
from cli_provenance_database_helpers import (
    latest_connector_fixture_provenance_database as _latest_connector_fixture_provenance_database,
)
from cli_provenance_database_helpers import missing_provenance_database as _missing_provenance_database
from cli_provenance_database_helpers import (
    two_run_provenance_database as _two_run_provenance_database,
)


runner = CliRunner()


def test_run_provenance_prints_latest_provenance(tmp_path: Path) -> None:
    database_path, _run = _latest_connector_fixture_provenance_database(tmp_path)

    result = runner.invoke(app, _run_provenance_args(database_path))

    assert result.exit_code == 0
    assert "Run Provenance - Run #1" in result.output
    assert "connector-fixture" in result.output
    assert "Example Approved API" in result.output
    assert "fixture_item_count" in result.output
    assert "Run provenance is local-only and read-only" in result.output


def test_run_provenance_prints_requested_run(tmp_path: Path) -> None:
    database_path, first, _second = _two_run_provenance_database(tmp_path)

    result = runner.invoke(
        app,
        _run_provenance_args(database_path, run_id=first.id),
    )

    assert result.exit_code == 0
    assert "Run Provenance - Run #1" in result.output
    assert "first" in result.output
    assert "second" not in result.output


def test_run_provenance_missing_provenance_prints_clear_message(tmp_path: Path) -> None:
    database_path = _missing_provenance_database(tmp_path)

    result = runner.invoke(app, _run_provenance_args(database_path))

    assert result.exit_code == 0
    assert "No run provenance found for run #1" in result.output
    assert "source mode: sample-data" in result.output
    assert "local-only and read-only" in result.output


def test_run_provenance_missing_manual_import_provenance_explains_legacy_gap(
    tmp_path: Path,
) -> None:
    database_path = _missing_provenance_database(tmp_path, source_mode="manual-import")

    result = runner.invoke(app, _run_provenance_args(database_path, run_id=1))

    assert result.exit_code == 0
    assert "No run provenance found for run #1" in result.output
    assert "source mode: manual-import" in result.output
    assert "may predate manual-import provenance recording" in result.output
    assert "Future wq daily --input-path runs record path-safe local input metadata" in result.output


def test_run_provenance_missing_database_does_not_create_database(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    result = runner.invoke(app, _run_provenance_args(database_path))

    assert result.exit_code == 0
    assert "No run provenance found." in result.output
    assert not database_path.exists()
    assert not database_path.parent.exists()
