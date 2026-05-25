import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_market_flow_database_helpers import buy_crossing_database as _buy_crossing_database
from cli_market_flow_database_helpers import single_buy_database as _single_buy_database
from cli_market_flow_database_helpers import small_mover_database as _small_mover_database
from cli_public_artifact_export_command_helpers import (
    export_args as _export_args,
    site_args as _site_args,
    site_bundle_args as _site_bundle_args,
    validate_intel_args as _validate_intel_args,
)
from cli_public_artifact_file_helpers import (
    write_minimal_invalid_public_intel as _write_minimal_invalid_public_intel,
    write_minimal_static_site as _write_minimal_static_site,
    write_public_intel_file as _write_public_intel_file,
    write_public_intel_missing_schema as _write_public_intel_missing_schema,
    write_public_intel_with_raw_inputs as _write_public_intel_with_raw_inputs,
)


runner = CliRunner()


def test_export_command_writes_public_intel(tmp_path: Path) -> None:
    database_path = _buy_crossing_database(tmp_path)
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _export_args(database_path, output_path),
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Wrote public intel export" in result.output
    assert "Stormglass Catalyst" in output_path.read_text(encoding="utf-8")


def test_export_command_uses_tuned_alert_settings(tmp_path: Path) -> None:
    database_path = _small_mover_database(tmp_path)
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _export_args(database_path, output_path, big_delta=20),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert payload["alerts"] == []


def test_export_command_handles_no_snapshots(tmp_path: Path) -> None:
    database_path = tmp_path / "empty.db"
    output_path = tmp_path / "public_intel.json"

    result = runner.invoke(
        app,
        _export_args(database_path, output_path),
    )

    assert result.exit_code == 0
    assert "No snapshots found." in result.output
    assert not output_path.exists()


def test_validate_intel_command_accepts_exported_public_intel(tmp_path: Path) -> None:
    database_path = _single_buy_database(tmp_path)
    output_path = tmp_path / "public_intel.json"
    runner.invoke(
        app,
        _export_args(database_path, output_path),
    )

    result = runner.invoke(app, _validate_intel_args(output_path))

    assert result.exit_code == 0
    assert "Public Intel Contract Validation" in result.output
    assert "Schema version" in result.output
    assert "1.0" in result.output
    assert "matches the local derived-only contract" in result.output


def test_validate_intel_command_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = _write_public_intel_with_raw_inputs(tmp_path)

    result = runner.invoke(app, _validate_intel_args(intel_path))

    assert result.exit_code != 0
    assert "Public Intel Contract Validation" in result.output
    assert "Raw/private field is not allowed" in result.output


def test_site_command_writes_index_html(tmp_path: Path) -> None:
    intel_path = _write_public_intel_file(tmp_path)
    output_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _site_args(intel_path, output_dir),
    )

    index_path = output_dir / "index.html"
    assert result.exit_code == 0
    assert index_path.exists()
    assert "Wrote local dashboard preview" in result.output
    assert "Stormglass Catalyst" in index_path.read_text(encoding="utf-8")


def test_site_command_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = _write_public_intel_missing_schema(tmp_path)
    output_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _site_args(intel_path, output_dir),
    )

    assert result.exit_code != 0
    assert "Public intel contract validation failed" in result.output
    assert "Missing required keys: schema_version" in result.output
    assert not (output_dir / "index.html").exists()


def test_site_command_handles_missing_public_intel(tmp_path: Path) -> None:
    output_dir = tmp_path / "site"

    result = runner.invoke(
        app,
        _site_args(tmp_path / "missing.json", output_dir),
    )

    assert result.exit_code == 0
    assert "No public intel export found. Run wq export first." in result.output
    assert not (output_dir / "index.html").exists()


def test_site_bundle_command_writes_local_bundle(tmp_path: Path) -> None:
    intel_path = _write_public_intel_file(tmp_path)
    site_dir = _write_minimal_static_site(tmp_path)
    output_dir = tmp_path / "bundle"

    result = runner.invoke(
        app,
        _site_bundle_args(intel_path, site_dir, output_dir),
    )

    assert result.exit_code == 0
    assert "Local Site Bundle" in result.output
    assert "wraeclast_quant_site_bundle.zip" in result.output
    assert (output_dir / "index.html").exists()
    assert (output_dir / "public_intel.json").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "wraeclast_quant_site_bundle.zip").exists()


def test_site_bundle_command_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = _write_minimal_invalid_public_intel(tmp_path)
    site_dir = _write_minimal_static_site(tmp_path)
    output_dir = tmp_path / "bundle"

    result = runner.invoke(
        app,
        _site_bundle_args(intel_path, site_dir, output_dir),
    )

    assert result.exit_code != 0
    assert "Public intel contract validation failed" in result.output
    assert not output_dir.exists()


def test_site_bundle_command_handles_missing_inputs(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        _site_bundle_args(
            tmp_path / "missing.json",
            tmp_path / "missing_site",
            tmp_path / "bundle",
        ),
    )

    assert result.exit_code != 0
    assert "No public intel export found. Run wq export first." in result.output
    assert not (tmp_path / "bundle").exists()
