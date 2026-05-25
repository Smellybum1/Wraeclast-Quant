from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_public_artifact_export_command_helpers import site_bundle_args as _site_bundle_args
from cli_public_artifact_file_helpers import (
    write_minimal_invalid_public_intel as _write_minimal_invalid_public_intel,
    write_minimal_static_site as _write_minimal_static_site,
    write_public_intel_file as _write_public_intel_file,
)


runner = CliRunner()


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
