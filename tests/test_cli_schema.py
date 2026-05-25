from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_resource_helpers import schema_args as _schema_args


runner = CliRunner()


def test_schema_command_prints_sqlite_schema_contract() -> None:
    result = runner.invoke(app, _schema_args())

    assert result.exit_code == 0
    assert "SQLite Schema Contract v2" in result.output
    assert "analysis_runs" in result.output
    assert "scored_opportunities" in result.output
    assert "report_artifacts" in result.output
    assert "recommendation_outcomes" in result.output
    assert "read-only" in result.output
