from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_connector_fixture_command_helpers import (
    connector_fixture_run_args as _connector_fixture_run_args,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    MANUAL_SNAPSHOT_TEMPLATE as _MANUAL_SNAPSHOT_TEMPLATE,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    currency_exchange_manual_snapshot_args as _currency_exchange_manual_snapshot_args,
)


runner = CliRunner()


def test_currency_exchange_manual_snapshot_output_feeds_fixture_runner(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "currency_exchange_fixture.json"
    write_result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(
            history_path=_MANUAL_SNAPSHOT_TEMPLATE,
            output_fixture_path=output_path,
        ),
    )

    run_result = runner.invoke(
        app,
        _connector_fixture_run_args(fixture_path=output_path),
    )

    assert write_result.exit_code == 0
    assert run_result.exit_code == 0
    assert "Connector Fixture Rows" in run_result.output
    assert "Chaos Orb / Divine Orb" in run_result.output
