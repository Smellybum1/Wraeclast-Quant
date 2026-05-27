from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation import (
    write_currency_exchange_ui_observation_manual_import,
)
from wraeclast_quant.commands.currency_exchange_ui_observation_rendering import (
    print_currency_exchange_ui_observation_export,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def register(app: typer.Typer) -> None:
    @app.command("currency-exchange-ui-observation")
    def currency_exchange_ui_observation(
        input_path: Path = typer.Option(
            ...,
            "--input-path",
            help="Local Currency Exchange UI observation JSON file.",
        ),
        output_path: Path = typer.Option(
            ...,
            "--output-path",
            help="Manual-import-compatible JSON output path.",
        ),
    ) -> None:
        try:
            result = write_currency_exchange_ui_observation_manual_import(
                input_path=input_path,
                output_path=output_path,
            )
        except ConnectorPolicyError as error:
            raise typer.BadParameter(str(error)) from error

        print_currency_exchange_ui_observation_export(result)


__all__ = ["register"]
