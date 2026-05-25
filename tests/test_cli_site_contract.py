import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_public_artifact_file_helpers import (
    write_publish_ready_bundle as _write_publish_ready_bundle,
)
from cli_public_artifact_publish_command_helpers import site_contract_args as _site_contract_args


runner = CliRunner()


def test_site_contract_ready_bundle_writes_json(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)
    output_path = tmp_path / "site_contract.json"

    result = runner.invoke(
        app,
        _site_contract_args(database_path, bundle_dir, output_path),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert "Public Site Contract" in result.output
    assert "ready" in result.output
    assert payload["schema_version"] == "1.0"
    assert payload["product"] == "Wraeclast Quant"
    assert payload["latest_database_run_id"] == run_id
    assert payload["artifact_run_ids"]["bundle"] == run_id
    assert payload["artifact_run_ids"]["public_intel"] == run_id
    assert payload["artifact_run_ids"]["static_site"] == run_id
    assert payload["publish_readiness"]["ready"] is True
    assert payload["safety"]["derived_only"] is True


def test_site_contract_strict_exits_nonzero_when_not_ready(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")
    output_path = tmp_path / "site_contract.json"

    result = runner.invoke(
        app,
        _site_contract_args(database_path, bundle_dir, output_path, strict=True),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.exit_code == 1
    assert output_path.exists()
    assert "not ready" in result.output
    assert payload["publish_readiness"]["ready"] is False
    assert "Public intel contract" in result.output
