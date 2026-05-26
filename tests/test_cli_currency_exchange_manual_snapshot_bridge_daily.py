from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_connector_fixture_command_helpers import (
    connector_fixture_export_args as _connector_fixture_export_args,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    MANUAL_SNAPSHOT_TEMPLATE as _MANUAL_SNAPSHOT_TEMPLATE,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    currency_exchange_manual_snapshot_args as _currency_exchange_manual_snapshot_args,
)
from cli_daily_command_helpers import daily_args as _daily_args


runner = CliRunner()


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
