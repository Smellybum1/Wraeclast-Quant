import json
from pathlib import Path

from typer.testing import CliRunner

from wraeclast_quant.cli import app
from cli_currency_exchange_manual_snapshot_helpers import (
    MANUAL_SNAPSHOT_TEMPLATE as _MANUAL_SNAPSHOT_TEMPLATE,
)
from cli_currency_exchange_manual_snapshot_helpers import (
    currency_exchange_manual_snapshot_args as _currency_exchange_manual_snapshot_args,
)


runner = CliRunner()


def test_currency_exchange_manual_snapshot_prints_rows() -> None:
    result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(),
    )

    assert result.exit_code == 0
    assert "Currency Exchange Manual Snapshot" in result.output
    assert "Chaos Orb / Divine Orb" in result.output
    assert "Manual snapshot rows: 2" in result.output
    assert "Next: wq currency-exchange-manual-snapshot --input-path" in result.output
    assert "--history-path <previous-snapshot>" in result.output
    assert "--output-fixture-path <fixture-output>" in result.output
    assert "No network requests were made" in result.output


def test_currency_exchange_manual_snapshot_writes_connector_fixture_with_history(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "currency_exchange_fixture.json"

    result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(
            history_path=_MANUAL_SNAPSHOT_TEMPLATE,
            output_fixture_path=output_path,
        ),
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert result.exit_code == 0
    assert "Wrote connector fixture" in result.output
    assert "Next: wq connector-fixture-export --review-path" in result.output
    assert "examples/reviews/pathofexile_currency_exchange_connector_review.json" in (
        result.output
    )
    assert "--fixture-path" in result.output
    assert output_path.name in result.output
    assert "--output-path <manual-import-output>" in result.output
    assert payload["source_name"] == "Path of Exile Currency Exchange API Preview"
    assert payload["items"][0]["signals"]["demand_momentum"] == 50.0


def test_currency_exchange_manual_snapshot_rejects_invalid_input(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid.json"
    input_path.write_text('{"markets": []}', encoding="utf-8")

    result = runner.invoke(
        app,
        _currency_exchange_manual_snapshot_args(input_path=input_path),
    )

    assert result.exit_code != 0
    assert "manual snapshot" in result.output
