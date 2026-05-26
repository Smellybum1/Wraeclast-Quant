from __future__ import annotations

import typer

from wraeclast_quant.commands import (
    connector_fixture_export,
    connector_fixture_inspection,
    connector_fixture_pipeline,
    currency_exchange_manual_snapshot,
)


def register(app: typer.Typer) -> None:
    connector_fixture_inspection.register(app)
    connector_fixture_export.register(app)
    connector_fixture_pipeline.register(app)
    currency_exchange_manual_snapshot.register(app)
