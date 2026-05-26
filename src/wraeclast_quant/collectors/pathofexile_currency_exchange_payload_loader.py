from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangePayload,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def load_currency_exchange_payload(path: str | Path) -> CurrencyExchangePayload:
    fixture_path = Path(path)
    try:
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read Currency Exchange fixture: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(f"Invalid Currency Exchange fixture JSON: {error}") from error

    try:
        return CurrencyExchangePayload.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(f"Invalid Currency Exchange fixture: {error}") from error


__all__ = ["load_currency_exchange_payload"]
