from __future__ import annotations

SIGNAL_FIELDS = [
    "demand_momentum",
    "build_dependency_score",
    "price_discount_score",
    "liquidity_score",
    "historical_spike_score",
    "patch_relevance_score",
    "manipulation_risk",
    "stale_data_penalty",
]


class ManualImportError(ValueError):
    """Raised when a local manual import file cannot be parsed or validated."""
