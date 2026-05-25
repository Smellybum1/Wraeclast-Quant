from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_resource_helpers import preflight_args as _preflight_args
from cli_resource_helpers import write_preflight_resources as _write_preflight_resources


runner = CliRunner()


def test_preflight_command_prints_table_and_summary(tmp_path: Path) -> None:
    resources_path = _write_preflight_resources(tmp_path)

    result = runner.invoke(
        app,
        _preflight_args(resources_path),
    )

    assert result.exit_code == 0
    assert "Connector Preflight" in result.output
    assert "Preflight Summary" in result.output
    assert "Approved API" in result.output
    assert "Ready for source-specific connector design" in result.output
    assert "Missing URL API" in result.output
    assert "missing a URL" in result.output
    assert "Official Discord" in result.output
    assert "discord-gated" in result.output
    assert "placeholder-only" in result.output
