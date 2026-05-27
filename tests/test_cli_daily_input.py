import hashlib
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
        _daily_args(
            input_path=input_path,
            database_path=database_path,
            brief_path=tmp_path / "market_brief.md",
            intel_path=tmp_path / "public_intel.json",
            site_dir=tmp_path / "site",
        ),
    )

    runs = SnapshotRepository(database_path).list_recent_runs(limit=10)
    assert result.exit_code == 0
    assert len(runs) == 1
    assert runs[0].source_mode == "manual-import"


def test_daily_input_path_records_local_manual_import_provenance(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")

    result = runner.invoke(
        app,
        _daily_args(
            input_path=input_path,
            database_path=database_path,
            brief_path=tmp_path / "market_brief.md",
            intel_path=tmp_path / "public_intel.json",
            site_dir=tmp_path / "site",
        ),
    )

    provenance = SnapshotRepository(database_path).run_provenance(1)
    assert result.exit_code == 0
    assert provenance is not None
    assert provenance.source_kind == "manual-import"
    assert provenance.resource_name == "Local manual import"
    assert provenance.access_method == "local-file"
    assert provenance.metadata["input_file_name"] == input_path.name
    assert provenance.metadata["input_path"] == "<absolute path omitted>"
    input_bytes = input_path.read_bytes()
    assert provenance.metadata["input_file_size_bytes"] == len(input_bytes)
    assert provenance.metadata["input_sha256"] == hashlib.sha256(input_bytes).hexdigest()
    assert provenance.metadata["manual_import_item_count"] == 1
    assert provenance.metadata["live_collection"] is False
    assert provenance.metadata["source_approval"] is False


def test_daily_input_path_run_provenance_cli_shows_redacted_local_metadata(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    input_path = _write_manual_import_json(tmp_path, "Manual Daily Catalyst")
    daily_result = runner.invoke(
        app,
        _daily_args(
            input_path=input_path,
            database_path=database_path,
            brief_path=tmp_path / "market_brief.md",
            intel_path=tmp_path / "public_intel.json",
            site_dir=tmp_path / "site",
        ),
    )

    provenance_result = runner.invoke(
        app,
        ["run-provenance", "--database-path", str(database_path), "--run-id", "1"],
    )

    assert daily_result.exit_code == 0
    assert provenance_result.exit_code == 0
    assert "Source kind" in provenance_result.output
    assert "manual-import" in provenance_result.output
    assert "input_file_name" in provenance_result.output
    assert "input_sha256" in provenance_result.output
    assert "<absolute path omitted>" in provenance_result.output
    assert "Run provenance is local-only and read-only" in provenance_result.output
