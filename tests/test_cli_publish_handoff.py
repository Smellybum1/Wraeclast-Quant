from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_public_artifact_file_helpers import (
    write_publish_ready_bundle as _write_publish_ready_bundle,
)
from cli_public_artifact_publish_command_helpers import publish_handoff_args as _publish_handoff_args


runner = CliRunner()


def test_publish_handoff_ready_bundle_writes_report(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "publish_handoff.md"

    result = runner.invoke(
        app,
        _publish_handoff_args(database_path, bundle_dir, output_path),
    )

    assert result.exit_code == 0
    assert "Manual Publish Handoff" in result.output
    assert "ready" in result.output
    report = output_path.read_text(encoding="utf-8")
    assert f"Latest database run: `#{run_id}`" in report
    assert "Manual Publishing Checklist" in report


def test_publish_handoff_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")
    output_path = tmp_path / "publish_handoff.md"

    result = runner.invoke(
        app,
        _publish_handoff_args(database_path, bundle_dir, output_path, strict=True),
    )

    assert result.exit_code == 1
    assert output_path.exists()
    assert "not ready" in result.output
    assert "Public intel contract" in output_path.read_text(encoding="utf-8")
