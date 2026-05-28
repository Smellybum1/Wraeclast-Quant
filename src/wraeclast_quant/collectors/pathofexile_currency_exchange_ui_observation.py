from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_formatting import (
    currency_name,
    format_ratio_value,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_models import (
    CurrencyExchangeUiObservation,
    CurrencyExchangeUiObservationExportResult,
    CurrencyExchangeUiObservationSnapshot,
    CurrencyExchangeUiStockRow,
    RatioValue,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_review import (
    currency_exchange_ui_observation_capture_review_flags,
    currency_exchange_ui_observation_review_flags,
    currency_exchange_ui_observation_review_notes,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_signals import (
    currency_exchange_ui_observation_signals,
    ratio_to_float,
    visible_ratio_spread_percent,
    visible_stock_total,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError


def load_currency_exchange_ui_observation(path: str | Path) -> CurrencyExchangeUiObservationSnapshot:
    observation_path = Path(path)
    try:
        raw = json.loads(observation_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read Currency Exchange UI observation: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange UI observation JSON: {error}"
        ) from error

    try:
        snapshot = CurrencyExchangeUiObservationSnapshot.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(
            f"Invalid Currency Exchange UI observation: {error}"
        ) from error
    if not snapshot.observations:
        raise ConnectorPolicyError("Invalid Currency Exchange UI observation: observations must not be empty.")
    return snapshot


def write_currency_exchange_ui_observation_manual_import(
    *,
    input_path: str | Path,
    output_path: str | Path,
    review_notes_output_path: str | Path | None = None,
) -> CurrencyExchangeUiObservationExportResult:
    snapshot = load_currency_exchange_ui_observation(input_path)
    payload = currency_exchange_ui_observation_manual_import_payload(snapshot)
    capture_review_flags = currency_exchange_ui_observation_capture_review_flags(snapshot)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    review_notes_path = None
    if review_notes_output_path is not None:
        review_notes_path = Path(review_notes_output_path)
        review_notes_path.parent.mkdir(parents=True, exist_ok=True)
        review_notes_path.write_text(
            currency_exchange_ui_observation_review_notes(snapshot),
            encoding="utf-8",
        )
    return CurrencyExchangeUiObservationExportResult(
        output_path=destination,
        item_count=len(payload["items"]),
        source_name="Path of Exile Currency Exchange UI Observation",
        review_notes_path=review_notes_path,
        capture_review_flag_count=len(capture_review_flags),
    )


def currency_exchange_ui_observation_manual_import_payload(
    snapshot: CurrencyExchangeUiObservationSnapshot,
) -> dict[str, list[dict[str, object]]]:
    totals = [visible_stock_total(observation) for observation in snapshot.observations]
    max_total = max(totals) if totals else 0
    return {
        "items": [
            currency_exchange_ui_observation_item(snapshot.league, observation, max_total)
            for observation in snapshot.observations
        ]
    }


def currency_exchange_ui_observation_item(
    default_league: str,
    observation: CurrencyExchangeUiObservation,
    max_visible_stock: int,
) -> dict[str, object]:
    signals = currency_exchange_ui_observation_signals(observation, max_visible_stock)
    league = observation.league or default_league
    return {
        "name": f"{currency_name(observation.want_currency)} / {currency_name(observation.have_currency)} ({league} UI)",
        "signals": signals.model_dump(),
    }


__all__ = [
    "CurrencyExchangeUiObservation",
    "CurrencyExchangeUiObservationExportResult",
    "CurrencyExchangeUiObservationSnapshot",
    "CurrencyExchangeUiStockRow",
    "currency_exchange_ui_observation_capture_review_flags",
    "currency_exchange_ui_observation_item",
    "currency_exchange_ui_observation_manual_import_payload",
    "currency_exchange_ui_observation_review_flags",
    "currency_exchange_ui_observation_review_notes",
    "currency_exchange_ui_observation_signals",
    "format_ratio_value",
    "load_currency_exchange_ui_observation",
    "ratio_to_float",
    "visible_ratio_spread_percent",
    "visible_stock_total",
    "write_currency_exchange_ui_observation_manual_import",
]
