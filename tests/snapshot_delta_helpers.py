from wraeclast_quant.storage.models import StoredOpportunityRecord


def stored_opportunity(name: str, score: float, action: str) -> StoredOpportunityRecord:
    return StoredOpportunityRecord(
        id=1,
        run_id=1,
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs={
            "demand_momentum": 0,
            "build_dependency_score": 0,
            "price_discount_score": 0,
            "liquidity_score": 0,
            "historical_spike_score": 0,
            "patch_relevance_score": 0,
            "manipulation_risk": 0,
            "stale_data_penalty": 0,
        },
    )


__all__ = ["stored_opportunity"]
