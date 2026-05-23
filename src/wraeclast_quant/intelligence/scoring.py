from __future__ import annotations

from pydantic import BaseModel, Field


class OpportunityInputs(BaseModel):
    demand_momentum: float = Field(ge=0, le=100)
    build_dependency_score: float = Field(ge=0, le=100)
    price_discount_score: float = Field(ge=0, le=100)
    liquidity_score: float = Field(ge=0, le=100)
    historical_spike_score: float = Field(ge=0, le=100)
    patch_relevance_score: float = Field(ge=0, le=100)
    manipulation_risk: float = Field(ge=0, le=100)
    stale_data_penalty: float = Field(ge=0, le=100)


class ScoredOpportunity(BaseModel):
    item_name: str
    opportunity_score: float
    action: str
    inputs: OpportunityInputs


def score_opportunity(inputs: OpportunityInputs) -> float:
    score = (
        inputs.demand_momentum * 0.20
        + inputs.build_dependency_score * 0.20
        + inputs.price_discount_score * 0.20
        + inputs.liquidity_score * 0.15
        + inputs.historical_spike_score * 0.10
        + inputs.patch_relevance_score * 0.10
        - inputs.manipulation_risk * 0.15
        - inputs.stale_data_penalty * 0.10
    )
    return round(max(0.0, min(100.0, score)), 2)


def action_for_score(score: float) -> str:
    if score >= 75:
        return "BUY"
    if score >= 55:
        return "WATCH"
    if score >= 35:
        return "HOLD / SELL SELECTIVELY"
    return "AVOID"

