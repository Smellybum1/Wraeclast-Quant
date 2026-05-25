from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_resource_helpers import collect_dry_run_args as _collect_dry_run_args


runner = CliRunner()


def test_collect_dry_run() -> None:
    result = runner.invoke(app, _collect_dry_run_args())

    assert result.exit_code == 0
    assert "POE2 Scout" in result.output
    assert "PriceSiteCollector" in result.output
