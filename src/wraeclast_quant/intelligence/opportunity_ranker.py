from wraeclast_quant.intelligence.scoring import (
    OpportunityInputs,
    ScoredOpportunity,
    action_for_score,
    score_opportunity,
)


def rank_opportunities(items: list[dict[str, object]]) -> list[ScoredOpportunity]:
    scored: list[ScoredOpportunity] = []
    for item in items:
        inputs = OpportunityInputs(**item["signals"])  # type: ignore[arg-type]
        score = score_opportunity(inputs)
        scored.append(
            ScoredOpportunity(
                item_name=str(item["name"]),
                opportunity_score=score,
                action=action_for_score(score),
                inputs=inputs,
            )
        )
    return sorted(scored, key=lambda opportunity: opportunity.opportunity_score, reverse=True)

