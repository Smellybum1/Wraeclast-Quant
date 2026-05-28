from __future__ import annotations

from typing import Any

from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import clamp_score
from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_models import (
    CurrencyExchangeUiObservation,
    RatioValue,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError
from wraeclast_quant.intelligence.scoring import OpportunityInputs


def currency_exchange_ui_observation_signals(
    observation: CurrencyExchangeUiObservation,
    max_visible_stock: int,
) -> OpportunityInputs:
    stock_total = visible_stock_total(observation)
    row_count = len(observation.stock_rows)
    spread = visible_ratio_spread_percent(observation)

    if stock_total <= 0:
        liquidity_score = 0.0 if observation.no_stock else 20.0
        demand_momentum = 20.0 if observation.no_stock else 35.0
        price_discount_score = 20.0 if observation.no_stock else 35.0
        stale_data_penalty = 25.0 if observation.no_stock else 15.0
    else:
        liquidity_score = clamp_score(15.0 + (stock_total / max(max_visible_stock, 1)) * 85.0)
        demand_momentum = clamp_score(35.0 + liquidity_score * 0.45 + min(row_count, 6) * 3.0)
        price_discount_score = clamp_score(65.0 - spread * 0.75)
        stale_data_penalty = 5.0

    manipulation_risk = clamp_score(
        (100.0 - liquidity_score) * 0.55
        + spread * 0.70
        + (25.0 if observation.no_stock else 0.0)
    )

    return OpportunityInputs(
        demand_momentum=demand_momentum,
        build_dependency_score=50.0,
        price_discount_score=price_discount_score,
        liquidity_score=liquidity_score,
        historical_spike_score=50.0,
        patch_relevance_score=50.0,
        manipulation_risk=manipulation_risk,
        stale_data_penalty=stale_data_penalty,
    )


def visible_stock_total(observation: CurrencyExchangeUiObservation) -> int:
    return sum(row.stock for row in observation.stock_rows)


def visible_ratio_spread_percent(observation: CurrencyExchangeUiObservation) -> float:
    ratios = [ratio_to_float(row.ratio) for row in observation.stock_rows]
    if not ratios:
        return 100.0 if observation.no_stock else 50.0

    baseline = ratio_to_float(observation.market_ratio) if observation.market_ratio is not None else ratios[0]
    if baseline <= 0:
        return 100.0
    return clamp_score(((max(ratios) - min(ratios)) / baseline) * 100.0)


def ratio_to_float(value: RatioValue) -> float:
    if isinstance(value, str):
        parts = [part.strip().replace(",", "") for part in value.split(":")]
        if len(parts) != 2:
            raise ConnectorPolicyError(f"Invalid ratio value: {value}")
        left = _positive_float(parts[0], value)
        right = _positive_float(parts[1], value)
        return left / right

    if isinstance(value, dict):
        if "want" not in value or "have" not in value:
            raise ConnectorPolicyError("Ratio objects must include want and have values.")
        left = _positive_float(value["want"], value)
        right = _positive_float(value["have"], value)
        return left / right

    raise ConnectorPolicyError(f"Invalid ratio value: {value}")


def _positive_float(value: Any, original: object) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ConnectorPolicyError(f"Invalid ratio value: {original}") from error
    if parsed <= 0:
        raise ConnectorPolicyError(f"Ratio values must be positive: {original}")
    return parsed


__all__ = [
    "currency_exchange_ui_observation_signals",
    "ratio_to_float",
    "visible_ratio_spread_percent",
    "visible_stock_total",
]
