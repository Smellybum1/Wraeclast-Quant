import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_connector_fixture_command_helpers import (
    connector_fixture_export_args as _connector_fixture_export_args,
    connector_fixture_run_args as _connector_fixture_run_args,
)
from cli_daily_command_helpers import daily_args as _daily_args
from cli_currency_exchange_manual_snapshot_helpers import (
    MANUAL_SNAPSHOT_TEMPLATE as _MANUAL_SNAPSHOT_TEMPLATE,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    currency_exchange_manual_snapshot_args as _currency_exchange_manual_snapshot_args,
)
from cli_manual_import_command_helpers import validate_import_args as _validate_import_args


runner = CliRunner()


def test_currency_exchange_manual_snapshot_prints_rows() -> None:
    result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(),
    )

    assert result.exit_code == 0
    assert "Currency Exchange Manual Snapshot" in result.output
    assert "Chaos Orb / Divine Orb" in result.output
    assert "Manual snapshot rows: 2" in result.output
    assert "No network requests were made" in result.output


def test_currency_exchange_manual_snapshot_writes_connector_fixture_with_history(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "currency_exchange_fixture.json"

    result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(
            history_path=_MANUAL_SNAPSHOT_TEMPLATE,
            output_fixture_path=output_path,
        ),
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Wrote connector fixture" in result.output
    assert payload["source_name"] == "Path of Exile Currency Exchange API Preview"
    assert payload["items"][0]["signals"]["demand_momentum"] == 50.0


def test_currency_exchange_manual_snapshot_output_feeds_fixture_runner(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "currency_exchange_fixture.json"
    write_result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(
            history_path=_MANUAL_SNAPSHOT_TEMPLATE,
            output_fixture_path=output_path,
        ),
    )

    run_result = runner.invoke(
        app,
        _connector_fixture_run_args(fixture_path=output_path),
    )

    assert write_result.exit_code == 0
    assert run_result.exit_code == 0
    assert "Connector Fixture Rows" in run_result.output
    assert "Chaos Orb / Divine Orb" in run_result.output


def test_currency_exchange_manual_snapshot_output_exports_to_manual_import(
    tmp_path: Path,
) -> None:
    fixture_path = tmp_path / "currency_exchange_fixture.json"
    import_path = tmp_path / "currency_exchange_manual_import.json"
    write_result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(
            history_path=_MANUAL_SNAPSHOT_TEMPLATE,
            output_fixture_path=fixture_path,
        ),
    )
    export_result = runner.invoke(
        app,
        _connector_fixture_export_args(
            fixture_path=fixture_path,
            output_path=import_path,
        ),
    )
    validate_result = runner.invoke(app, _validate_import_args(import_path))
    payload = json.loads(import_path.read_text(encoding="utf-8"))

    assert write_result.exit_code == 0
    assert export_result.exit_code == 0
    assert validate_result.exit_code == 0
    assert payload["items"][0]["name"] == "Chaos Orb / Divine Orb"
    assert "signals" in payload["items"][0]


def test_currency_exchange_manual_snapshot_output_runs_daily_pipeline(
    tmp_path: Path,
) -> None:
    fixture_path = tmp_path / "currency_exchange_fixture.json"
    import_path = tmp_path / "currency_exchange_manual_import.json"
    database_path = tmp_path / "snapshots.db"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(
            history_path=_MANUAL_SNAPSHOT_TEMPLATE,
            output_fixture_path=fixture_path,
        ),
    )
    runner.invoke(
        app,
        _connector_fixture_export_args(
            fixture_path=fixture_path,
            output_path=import_path,
        ),
    )

    daily_result = runner.invoke(
        app,
        _daily_args(
            input_path=import_path,
            database_path=database_path,
            intel_path=intel_path,
            site_dir=site_dir,
        ),
    )
    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    intel_text = intel_path.read_text(encoding="utf-8")

    assert daily_result.exit_code == 0
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"
    assert "Chaos Orb / Divine Orb" in intel_text
    assert "Chaos Orb / Divine Orb" in (site_dir / "index.html").read_text(encoding="utf-8")


def test_currency_exchange_manual_snapshot_rejects_invalid_input(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid.json"
    input_path.write_text('{"markets": []}', encoding="utf-8")

    result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(input_path=input_path),
    )

    assert result.exit_code != 0
    assert "manual snapshot" in result.output
