def manual_import_item(name: str) -> dict[str, object]:
    return {
        "name": name,
        "signals": {
            "demand_momentum": 88.0,
            "build_dependency_score": 82.0,
            "price_discount_score": 76.0,
            "liquidity_score": 70.0,
            "historical_spike_score": 68.0,
            "patch_relevance_score": 74.0,
            "manipulation_risk": 18.0,
            "stale_data_penalty": 8.0,
        },
    }
