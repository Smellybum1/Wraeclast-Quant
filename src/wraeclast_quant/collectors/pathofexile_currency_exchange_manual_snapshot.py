from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from wraeclast_quant.collectors.pathofexile_currency_exchange_manual_conversion import (
    currency_exchange_market_from_manual_market,
    currency_exchange_payload_from_manual_snapshot,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeManualSnapshot,
    CurrencyExchangePayload,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def load_currency_exchange_manual_snapshot(path: str | Path) -> CurrencyExchangePayload:
    snapshot_path = Path(path)
    try:
        raw = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read Currency Exchange manual snapshot: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange manual snapshot JSON: {error}"
        ) from error

    try:
        snapshot = CurrencyExchangeManualSnapshot.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange manual snapshot: {error}"
        ) from error
    return currency_exchange_payload_from_manual_snapshot(snapshot)


__all__ = [
    "currency_exchange_market_from_manual_market",
    "currency_exchange_payload_from_manual_snapshot",
    "load_currency_exchange_manual_snapshot",
]
