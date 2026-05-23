def build_signal_label(score: float) -> str:
    if score >= 75:
        return "build-defining"
    if score >= 45:
        return "notable"
    return "niche"

