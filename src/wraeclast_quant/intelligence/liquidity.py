def liquidity_label(score: float) -> str:
    if score >= 75:
        return "high"
    if score >= 45:
        return "medium"
    return "thin"

