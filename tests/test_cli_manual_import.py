from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_manual_import_command_helpers import (
    import_args as _import_args,
    inspect_import_args as _inspect_import_args,
)
from cli_manual_import_file_helpers import write_invalid_manual_import_json as _write_invalid_manual_import_json
from cli_manual_import_file_helpers import write_manual_import_csv as _write_manual_import_csv
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


runner = CliRunner()


def test_import_json_records_manual_import_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(
        app,
        _import_args(input_path, database_path),
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert "Imported Opportunities" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "Recorded manual import run" in result.output
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"


def test_import_csv_records_manual_import_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_csv(tmp_path)

    result = runner.invoke(
        app,
        _import_args(input_path, database_path),
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert "Ashen Rune Core" in result.output
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"


def test_import_invalid_input_exits_nonzero(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_invalid_manual_import_json(tmp_path)

    result = runner.invoke(
        app,
        _import_args(input_path, database_path),
    )

    assert result.exit_code != 0
    assert "demand_momentum" in result.output


def test_inspect_import_prints_read_only_diagnostics(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst", "Ashen Rune Core")

    result = runner.invoke(app, _inspect_import_args(input_path))

    assert result.exit_code == 0
    assert "Manual Import Diagnostics" in result.output
    assert "Items" in result.output
    assert "2" in result.output
    assert "Average score" in result.output
    assert "Signal Averages" in result.output
    assert "Top Imported Opportunities" in result.output
    assert "Stormglass Catalyst" in result.output
    assert "read-only" in result.output


def test_inspect_import_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = _write_manual_import_json(tmp_path, "Stormglass Catalyst")

    result = runner.invoke(app, _inspect_import_args(input_path))

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()


def test_inspect_import_invalid_input_exits_nonzero(tmp_path: Path) -> None:
    input_path = _write_invalid_manual_import_json(tmp_path)

    result = runner.invoke(app, _inspect_import_args(input_path))

    assert result.exit_code != 0
    assert "demand_momentum" in result.output
