from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.collectors.pathofexile_currency_exchange import (
    CurrencyExchangePayload,
    load_currency_exchange_manual_snapshot,
    preview_currency_exchange_signal_fixture_from_baseline,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_fixture import (
    currency_exchange_fixture_from_payload,
)
from wraeclast_quant.config.connector_fixture_models import ConnectorFixture


def run_currency_exchange_manual_snapshot_workflow(
    *,
    input_path: Path,
    history_path: Path | None,
    output_fixture_path: Path | None,
) -> ConnectorFixture:
    payload = load_currency_exchange_manual_snapshot(input_path)
    fixture = currency_exchange_fixture_for_manual_snapshot(payload, history_path)
    if output_fixture_path is not None:
        write_currency_exchange_connector_fixture(output_fixture_path, fixture)
    return fixture


def currency_exchange_fixture_for_manual_snapshot(
    payload: CurrencyExchangePayload,
    history_path: Path | None,
) -> ConnectorFixture:
    if history_path is None:
        return currency_exchange_fixture_from_payload(payload)
    history = [load_currency_exchange_manual_snapshot(history_path)]
    return preview_currency_exchange_signal_fixture_from_baseline(payload, history)


def write_currency_exchange_connector_fixture(
    output_path: Path,
    fixture: ConnectorFixture,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(fixture.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "currency_exchange_fixture_for_manual_snapshot",
    "run_currency_exchange_manual_snapshot_workflow",
    "write_currency_exchange_connector_fixture",
]
