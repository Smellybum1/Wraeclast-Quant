from __future__ import annotations

import json
from pathlib import Path

import typer

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    load_currency_exchange_manual_snapshot,
    preview_currency_exchange_signal_fixture_from_baseline,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_fixture import (
    currency_exchange_fixture_from_payload,
)
from wraeclast_quant.commands._connector_support import console
from wraeclast_quant.commands.currency_exchange_manual_snapshot_rendering import (
    print_currency_exchange_manual_snapshot,
)
from wraeclast_quant.config.connector_fixture_models import ConnectorFixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def register(app: typer.Typer) -> None:
    @app.command("currency-exchange-manual-snapshot")
    def currency_exchange_manual_snapshot(
        input_path: Path = typer.Option(
            ...,
            "--input-path",
            help="Local Currency Exchange manual snapshot JSON file.",
        ),
        history_path: Path | None = typer.Option(
            None,
            "--history-path",
            help="Optional previous manual snapshot JSON for preview baseline diagnostics.",
        ),
        output_fixture_path: Path | None = typer.Option(
            None,
            "--output-fixture-path",
            help="Optional connector-fixture JSON output path.",
        ),
    ) -> None:
        try:
            payload = load_currency_exchange_manual_snapshot(input_path)
            fixture = _fixture_for_manual_snapshot(payload, history_path)
            if output_fixture_path is not None:
                _write_fixture(output_fixture_path, fixture)
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_currency_exchange_manual_snapshot(
            fixture=fixture,
            input_path=input_path,
            history_path=history_path,
            output_fixture_path=output_fixture_path,
        )


def _fixture_for_manual_snapshot(
    payload,
    history_path: Path | None,
) -> ConnectorFixture:
    if history_path is None:
        return currency_exchange_fixture_from_payload(payload)
    history = [load_currency_exchange_manual_snapshot(history_path)]
    return preview_currency_exchange_signal_fixture_from_baseline(payload, history)


def _write_fixture(output_path: Path, fixture: ConnectorFixture) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(fixture.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = ["register"]
