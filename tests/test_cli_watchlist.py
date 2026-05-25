from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_report_helpers import watchlist_args as _watchlist_args


runner = CliRunner()


def test_watchlist() -> None:
    result = runner.invoke(app, _watchlist_args())

    assert result.exit_code == 0
    assert "Watchlist" in result.output
