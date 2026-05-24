from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.market_brief_models import (
    REQUIRED_MARKET_BRIEF_MARKERS,
    MarketBriefHealthResult,
)


def check_market_brief_health(
    path: Path = Path("data/processed/market_brief.md"),
) -> MarketBriefHealthResult | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    missing_markers = [
        name
        for name, marker in sorted(REQUIRED_MARKET_BRIEF_MARKERS.items())
        if marker not in text
    ]
    return MarketBriefHealthResult(
        path=path,
        valid=not missing_markers,
        missing_markers=missing_markers,
        includes_snapshot_changes="## Snapshot Changes" in text,
        size_bytes=path.stat().st_size,
    )
