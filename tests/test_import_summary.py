from wraeclast_quant.importers.summary import summarize_opportunities
from wraeclast_quant.intelligence.scoring import OpportunityInputs, ScoredOpportunity


def test_summarize_opportunities_calculates_score_and_action_summary() -> None:
    summary = summarize_opportunities(
        [
            _opportunity("High", 80.0, "BUY", demand_momentum=90, liquidity_score=70),
            _opportunity("Mid", 60.0, "WATCH", demand_momentum=70, liquidity_score=50),
            _opportunity("Low", 30.0, "AVOID", demand_momentum=20, liquidity_score=30),
        ]
    )

    assert summary.item_count == 3
    assert summary.min_score == 30.0
    assert summary.max_score == 80.0
    assert summary.average_score == 56.67
    assert summary.action_counts == {"AVOID": 1, "BUY": 1, "WATCH": 1}
    assert summary.signal_averages["demand_momentum"] == 60.0
    assert summary.signal_averages["liquidity_score"] == 50.0


def test_summarize_opportunities_handles_empty_list() -> None:
    summary = summarize_opportunities([])

    assert summary.item_count == 0
    assert summary.action_counts == {}
    assert summary.average_score == 0.0
    assert summary.signal_averages["demand_momentum"] == 0.0


def _opportunity(
    name: str,
    score: float,
    action: str,
    *,
    demand_momentum: float = 0.0,
    liquidity_score: float = 0.0,
) -> ScoredOpportunity:
    return ScoredOpportunity(
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs=OpportunityInputs(
            demand_momentum=demand_momentum,
            build_dependency_score=0,
            price_discount_score=0,
            liquidity_score=liquidity_score,
            historical_spike_score=0,
            patch_relevance_score=0,
            manipulation_risk=0,
            stale_data_penalty=0,
        ),
    )
