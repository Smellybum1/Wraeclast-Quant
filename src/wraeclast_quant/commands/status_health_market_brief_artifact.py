from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.market_brief import MarketBriefHealthResult


def market_brief_status(health: MarketBriefHealthResult | None) -> str:
    if health is None:
        return "no"
    return "ok" if health.valid else "needs attention"


def market_brief_details(
    path: Path,
    health: MarketBriefHealthResult | None,
) -> str:
    if health is None:
        return str(path)
    if not health.valid:
        return f"{health.path}; missing markers: {', '.join(health.missing_markers)}"
    snapshot = "with snapshot changes" if health.includes_snapshot_changes else "no snapshot changes"
    return f"{health.path}; {snapshot}; {health.size_bytes} bytes"
