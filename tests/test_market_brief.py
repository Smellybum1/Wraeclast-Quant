from wraeclast_quant.intelligence.snapshot_deltas import compare_opportunities
from wraeclast_quant.intelligence.scoring import OpportunityInputs, ScoredOpportunity
from wraeclast_quant.reports.market_brief import (
    check_market_brief_health,
    render_market_brief,
    write_market_brief,
)
from wraeclast_quant.storage.models import StoredOpportunityRecord


def test_report_renders_without_comparison() -> None:
    report = render_market_brief([_opportunity("Stormglass Catalyst", 70.4, "WATCH")])

    assert "Wraeclast Quant Market Brief" in report
    assert "Snapshot Changes" not in report


def test_report_includes_top_movers() -> None:
    comparison = compare_opportunities(
        previous=[_stored("Stormglass Catalyst", 50.0, "HOLD / SELL SELECTIVELY")],
        latest=[_stored("Stormglass Catalyst", 76.0, "BUY")],
        previous_run_id=1,
        latest_run_id=2,
    )

    report = render_market_brief(
        [_opportunity("Stormglass Catalyst", 76.0, "BUY")],
        comparison=comparison,
    )

    assert "## Snapshot Changes" in report
    assert "### Top Score Movers" in report
    assert "| Stormglass Catalyst | 50.00 | 76.00 | +26.00 | BUY |" in report


def test_report_includes_action_new_and_removed_changes() -> None:
    comparison = compare_opportunities(
        previous=[
            _stored("Removed Relic", 42.0, "HOLD / SELL SELECTIVELY"),
            _stored("Stormglass Catalyst", 50.0, "HOLD / SELL SELECTIVELY"),
        ],
        latest=[
            _stored("New Catalyst", 60.0, "WATCH"),
            _stored("Stormglass Catalyst", 76.0, "BUY"),
        ],
        previous_run_id=1,
        latest_run_id=2,
    )

    report = render_market_brief(
        [_opportunity("Stormglass Catalyst", 76.0, "BUY")],
        comparison=comparison,
    )

    assert "### Action Changes / New / Removed" in report
    assert "| New Catalyst | new |  | WATCH |  |" in report
    assert "| Removed Relic | removed | HOLD / SELL SELECTIVELY |  |  |" in report
    assert "| Stormglass Catalyst | changed | HOLD / SELL SELECTIVELY | BUY | +26.00 |" in report


def test_report_includes_stable_message_when_no_changes() -> None:
    comparison = compare_opportunities(
        previous=[_stored("Stormglass Catalyst", 70.4, "WATCH")],
        latest=[_stored("Stormglass Catalyst", 70.4, "WATCH")],
        previous_run_id=1,
        latest_run_id=2,
    )

    report = render_market_brief(
        [_opportunity("Stormglass Catalyst", 70.4, "WATCH")],
        comparison=comparison,
    )

    assert "## Snapshot Changes" in report
    assert "No score, action, new, or removed item changes were detected." in report


def test_check_market_brief_health_reports_valid_brief(tmp_path) -> None:
    path = write_market_brief(
        [_opportunity("Stormglass Catalyst", 70.4, "WATCH")],
        path=tmp_path / "market_brief.md",
    )

    health = check_market_brief_health(path)

    assert health is not None
    assert health.valid is True
    assert health.missing_markers == []
    assert health.includes_snapshot_changes is False
    assert health.size_bytes > 0


def test_check_market_brief_health_reports_missing_markers(tmp_path) -> None:
    path = tmp_path / "market_brief.md"
    path.write_text("# Not A Brief", encoding="utf-8")

    health = check_market_brief_health(path)

    assert health is not None
    assert health.valid is False
    assert "title" in health.missing_markers
    assert "recommendation-table" in health.missing_markers


def test_check_market_brief_health_missing_file_returns_none(tmp_path) -> None:
    assert check_market_brief_health(tmp_path / "missing.md") is None


def _stored(name: str, score: float, action: str) -> StoredOpportunityRecord:
    return StoredOpportunityRecord(
        id=1,
        run_id=1,
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs={
            "demand_momentum": 0,
            "build_dependency_score": 0,
            "price_discount_score": 0,
            "liquidity_score": 0,
            "historical_spike_score": 0,
            "patch_relevance_score": 0,
            "manipulation_risk": 0,
            "stale_data_penalty": 0,
        },
    )


def _opportunity(name: str, score: float, action: str) -> ScoredOpportunity:
    return ScoredOpportunity(
        item_name=name,
        opportunity_score=score,
        action=action,
        inputs=OpportunityInputs(
            demand_momentum=0,
            build_dependency_score=0,
            price_discount_score=0,
            liquidity_score=0,
            historical_spike_score=0,
            patch_relevance_score=0,
            manipulation_risk=0,
            stale_data_penalty=0,
        ),
    )
