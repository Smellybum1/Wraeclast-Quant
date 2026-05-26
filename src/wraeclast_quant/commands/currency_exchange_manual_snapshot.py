from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.currency_exchange_manual_snapshot_rendering import (
    print_currency_exchange_manual_snapshot,
)
from wraeclast_quant.commands.currency_exchange_manual_snapshot_workflow import (
    run_currency_exchange_manual_snapshot_workflow,
)
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
            fixture = run_currency_exchange_manual_snapshot_workflow(
                input_path=input_path,
                history_path=history_path,
                output_fixture_path=output_fixture_path,
            )
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_currency_exchange_manual_snapshot(
            fixture=fixture,
            input_path=input_path,
            history_path=history_path,
            output_fixture_path=output_fixture_path,
        )


__all__ = ["register"]
