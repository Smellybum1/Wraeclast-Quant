from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_metrics import clamp_score
from wraeclast_quant.collectors.pathofexile_currency_exchange_models import (
    CurrencyExchangeBaselineDiagnostics,
)
from wraeclast_quant.intelligence.scoring import OpportunityInputs


def preview_currency_exchange_opportunity_inputs(
    diagnostic: CurrencyExchangeBaselineDiagnostics,
) -> OpportunityInputs | None:
    if diagnostic.confidence != "preview" or diagnostic.blockers:
        return None

    manipulation_risk = clamp_score(
        (100.0 - diagnostic.liquidity_index) * 0.5 + diagnostic.spread_index * 0.5
    )
    return OpportunityInputs(
        demand_momentum=diagnostic.demand_index,
        build_dependency_score=50.0,
        price_discount_score=50.0,
        liquidity_score=diagnostic.liquidity_index,
        historical_spike_score=50.0,
        patch_relevance_score=50.0,
        manipulation_risk=manipulation_risk,
        stale_data_penalty=diagnostic.stale_data_penalty,
    )


__all__ = ["preview_currency_exchange_opportunity_inputs"]
