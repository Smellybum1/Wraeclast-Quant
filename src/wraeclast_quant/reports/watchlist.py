from wraeclast_quant.intelligence.scoring import ScoredOpportunity


def top_watchlist(opportunities: list[ScoredOpportunity], limit: int = 5) -> list[ScoredOpportunity]:
    return sorted(opportunities, key=lambda item: item.opportunity_score, reverse=True)[:limit]

