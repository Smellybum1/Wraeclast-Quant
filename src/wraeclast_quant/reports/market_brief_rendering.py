from __future__ import annotations

from pathlib import Path

from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison
from wraeclast_quant.reports.market_brief_sections import (
    render_opportunities_section,
    render_snapshot_changes_section,
)


def render_market_brief(
    opportunities: list[ScoredOpportunity],
    comparison: SnapshotComparison | None = None,
) -> str:
    lines = render_opportunities_section(opportunities)
    if comparison is not None:
        lines.extend(render_snapshot_changes_section(comparison))
    return "\n".join(lines)


def write_market_brief(
    opportunities: list[ScoredOpportunity],
    path: Path = Path("data/processed/market_brief.md"),
    comparison: SnapshotComparison | None = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_market_brief(opportunities, comparison=comparison), encoding="utf-8")
    return path


__all__ = ["render_market_brief", "write_market_brief"]
