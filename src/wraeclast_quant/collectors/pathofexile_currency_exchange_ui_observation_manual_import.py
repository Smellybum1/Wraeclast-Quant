from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_formatting import (
    currency_name,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_models import (
    CurrencyExchangeUiObservation,
    CurrencyExchangeUiObservationSnapshot,
)
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_signals import (
    currency_exchange_ui_observation_signals,
    visible_stock_total,
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
    "currency_exchange_ui_observation_item",
    "currency_exchange_ui_observation_manual_import_payload",
]
