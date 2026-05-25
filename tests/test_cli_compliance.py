from typer.testing import CliRunner

from wraeclast_quant.cli import app

from cli_resource_helpers import compliance_args as _compliance_args


runner = CliRunner()


def test_compliance_command_uses_real_resources() -> None:
    result = runner.invoke(app, _compliance_args())

    assert result.exit_code == 0
    assert "Resource Compliance" in result.output
    assert "POE2 Scout Currency" in result.output
    assert "Official Path of Exile 2 Discord" in result.output
