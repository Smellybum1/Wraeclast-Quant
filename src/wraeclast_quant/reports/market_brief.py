from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.intelligence.snapshot_deltas import SnapshotComparison
from wraeclast_quant.intelligence.scoring import ScoredOpportunity

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


def render_market_brief(
    opportunities: list[ScoredOpportunity],
    comparison: SnapshotComparison | None = None,
) -> str:
    lines = [
        "# Wraeclast Quant Market Brief",
        "",
        "Research output only. The user must manually review and execute any trades.",
        "",
        "| Rank | Item | Score | Action |",
        "| --- | --- | ---: | --- |",
    ]
    for index, opportunity in enumerate(opportunities, start=1):
        lines.append(
            f"| {index} | {opportunity.item_name} | "
            f"{opportunity.opportunity_score:.2f} | {opportunity.action} |"
        )
    lines.append("")
    if comparison is not None:
        lines.extend(_render_snapshot_changes(comparison))
    return "\n".join(lines)


def write_market_brief(
    opportunities: list[ScoredOpportunity],
    path: Path = Path("data/processed/market_brief.md"),
    comparison: SnapshotComparison | None = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_market_brief(opportunities, comparison=comparison), encoding="utf-8")
    return path


def check_market_brief_health(path: Path = Path("data/processed/market_brief.md")) -> MarketBriefHealthResult | None:
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


def _render_snapshot_changes(comparison: SnapshotComparison, limit: int = 5) -> list[str]:
    lines = [
        "## Snapshot Changes",
        "",
        f"Compared run #{comparison.latest_run_id} against run #{comparison.previous_run_id}.",
        "",
    ]
    top_movers = comparison.top_movers[:limit]
    status_changes = comparison.status_changes[:limit]
    if not top_movers and not status_changes:
        lines.extend(["No score, action, new, or removed item changes were detected.", ""])
        return lines

    if top_movers:
        lines.extend(
            [
                "### Top Score Movers",
                "",
                "| Item | Previous | Latest | Delta | Action |",
                "| --- | ---: | ---: | ---: | --- |",
            ]
        )
        for delta in top_movers:
            lines.append(
                f"| {delta.item_name} | {_format_score(delta.previous_score)} | "
                f"{_format_score(delta.latest_score)} | {_format_delta(delta.score_delta)} | "
                f"{delta.latest_action or ''} |"
            )
        lines.append("")

    if status_changes:
        lines.extend(
            [
                "### Action Changes / New / Removed",
                "",
                "| Item | Status | Previous Action | Latest Action | Delta |",
                "| --- | --- | --- | --- | ---: |",
            ]
        )
        for delta in status_changes:
            lines.append(
                f"| {delta.item_name} | {delta.status} | {delta.previous_action or ''} | "
                f"{delta.latest_action or ''} | {_format_delta(delta.score_delta)} |"
            )
        lines.append("")

    return lines


def _format_score(score: float | None) -> str:
    if score is None:
        return ""
    return f"{score:.2f}"


def _format_delta(delta: float | None) -> str:
    if delta is None:
        return ""
    return f"{delta:+.2f}"
