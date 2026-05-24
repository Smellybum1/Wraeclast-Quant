from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_resource_helpers import collect_dry_run_args as _collect_dry_run_args
from cli_resource_helpers import compliance_args as _compliance_args
from cli_resource_helpers import preflight_args as _preflight_args
from cli_resource_helpers import schema_args as _schema_args
from cli_resource_helpers import write_preflight_resources as _write_preflight_resources


runner = CliRunner()


def test_collect_dry_run() -> None:
    result = runner.invoke(app, _collect_dry_run_args())

    assert result.exit_code == 0
    assert "POE2 Scout" in result.output
    assert "PriceSiteCollector" in result.output


def test_compliance_command_uses_real_resources() -> None:
    result = runner.invoke(app, _compliance_args())

    assert result.exit_code == 0
    assert "Resource Compliance" in result.output
    assert "POE2 Scout Currency" in result.output
    assert "Official Path of Exile 2 Discord" in result.output


def test_schema_command_prints_sqlite_schema_contract() -> None:
    result = runner.invoke(app, _schema_args())

    assert result.exit_code == 0
    assert "SQLite Schema Contract v2" in result.output
    assert "analysis_runs" in result.output
    assert "scored_opportunities" in result.output
    assert "report_artifacts" in result.output
    assert "recommendation_outcomes" in result.output
    assert "read-only" in result.output


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
