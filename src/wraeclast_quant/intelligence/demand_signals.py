def demand_label(score: float) -> str:
    if score >= 75:
        return "rising"
    if score >= 45:
        return "steady"
    return "soft"

