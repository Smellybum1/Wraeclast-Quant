from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REQUIRED_MARKET_BRIEF_MARKERS = {
    "title": "# Wraeclast Quant Market Brief",
    "research-boundary": "Research output only.",
    "recommendation-table": "| Rank | Item | Score | Action |",
}


@dataclass(frozen=True)
class MarketBriefHealthResult:
    path: Path
    valid: bool
    missing_markers: list[str]
    includes_snapshot_changes: bool
    size_bytes: int
