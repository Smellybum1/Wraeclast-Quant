from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_public_artifact_export_command_helpers import site_args as _site_args
from cli_public_artifact_file_helpers import (
    write_public_intel_file as _write_public_intel_file,
    write_public_intel_missing_schema as _write_public_intel_missing_schema,
)


runner = CliRunner()


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
