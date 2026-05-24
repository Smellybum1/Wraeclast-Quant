import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from wraeclast_quant.storage.repositories import SnapshotRepository

from cli_daily_command_helpers import daily_args as _daily_args
from cli_daily_command_helpers import schedule_helper_args as _schedule_helper_args
from cli_daily_fixture_helpers import previous_stormglass_database as _previous_stormglass_database
from cli_daily_fixture_helpers import small_mover_daily_setup as _small_mover_daily_setup
from cli_doc_markdown_helpers import documented_bullets as _documented_bullets
from cli_manual_import_file_helpers import (
    write_invalid_manual_import_json as _write_invalid_manual_import_json,
)
from cli_manual_import_file_helpers import write_manual_import_json as _write_manual_import_json


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


def test_daily_creates_exactly_one_analysis_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"

    result = runner.invoke(
        app,
        _daily_args(sample_data=True, database_path=database_path),
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


def test_daily_pipeline_contract_doc_matches_printed_output_labels(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    brief_path = tmp_path / "market_brief.md"
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    doc_text = Path("docs/DAILY_PIPELINE.md").read_text(encoding="utf-8")
    output_labels = _documented_bullets(doc_text, "Successful daily runs print these output labels:")

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
    assert output_labels == {"Database", "Market brief", "Public intel", "Dashboard"}
    for label in output_labels:
        assert f"{label}:" in result.output
    assert "Daily run #1 complete." in result.output


def test_daily_rejects_sample_data_and_input_path(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _daily_args(
            sample_data=True,
            input_path=input_path,
            database_path=tmp_path / "snapshots.db",
        ),
    )

    assert result.exit_code != 0
    assert "Use either --sample-data or --input-path, not both." in result.output


def test_daily_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path, input_path = _small_mover_daily_setup(tmp_path)

    result = runner.invoke(
        app,
        _daily_args(input_path=input_path, database_path=database_path, big_delta=20),
    )

    assert result.exit_code == 0
    assert "No alert candidates found." in result.output


def test_daily_requires_sample_data_or_input_path(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _daily_args(database_path=tmp_path / "snapshots.db"),
    )

    assert result.exit_code != 0
    assert "Use --sample-data or --input-path for daily runs." in result.output


def test_schedule_helper_sample_data_prints_scheduler_guidance() -> None:
    result = runner.invoke(app, _schedule_helper_args(sample_data=True, time="09:30"))

    assert result.exit_code == 0
    assert "Daily command:" in result.output
    assert "wq daily --sample-data" in result.output
    assert "schtasks /Create" in result.output
    assert "/ST 09:30" in result.output
    assert "PowerShell one-liner alternative:" in result.output
    assert "does not create scheduled tasks" in result.output


def test_schedule_helper_input_path_validates_and_prints_daily_command(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _schedule_helper_args(input_path=input_path),
    )

    assert result.exit_code == 0
    assert "wq daily --input-path" in result.output
    assert str(input_path) in result.output
    assert "schtasks /Create" in result.output


def test_schedule_helper_rejects_sample_data_and_input_path(tmp_path: Path) -> None:
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _schedule_helper_args(sample_data=True, input_path=input_path),
    )

    assert result.exit_code != 0
    assert "Use either --sample-data or --input-path, not both." in result.output


def test_schedule_helper_requires_sample_data_or_input_path() -> None:
    result = runner.invoke(app, _schedule_helper_args())

    assert result.exit_code != 0
    assert "Use --sample-data or --input-path for schedule helper." in result.output


def test_schedule_helper_rejects_invalid_time() -> None:
    result = runner.invoke(app, _schedule_helper_args(sample_data=True, time="25:99"))

    assert result.exit_code != 0
    assert "Use --time in HH:MM 24-hour format." in result.output


def test_schedule_helper_rejects_invalid_import_file(tmp_path: Path) -> None:
    input_path = _write_invalid_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _schedule_helper_args(input_path=input_path),
    )

    assert result.exit_code != 0
    assert "demand_momentum" in result.output


def test_schedule_helper_does_not_create_database(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, _schedule_helper_args(sample_data=True))

    assert result.exit_code == 0
    assert not Path("data/wraeclast_quant.db").exists()
