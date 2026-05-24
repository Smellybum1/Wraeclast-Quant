from __future__ import annotations

from wraeclast_quant.intelligence.scoring import OpportunityInputs, ScoredOpportunity


def opportunity(name: str, score: float, action: str) -> ScoredOpportunity:
    return ScoredOpportunity(
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs=OpportunityInputs(
            demand_momentum=0,
            build_dependency_score=0,
            price_discount_score=0,
            liquidity_score=0,
            historical_spike_score=0,
            patch_relevance_score=0,
            manipulation_risk=0,
            stale_data_penalty=0,
        ),
    )


def manual_item(name: str) -> dict[str, object]:
    return {
        "name": name,
        "signals": {
            "demand_momentum": 88,
            "build_dependency_score": 82,
            "price_discount_score": 76,
            "liquidity_score": 70,
            "historical_spike_score": 68,
            "patch_relevance_score": 74,
            "manipulation_risk": 18,
            "stale_data_penalty": 8,
        },
    }
