from wraeclast_quant.reports.market_brief import (
    check_market_brief_health,
    write_market_brief,
)

from market_brief_helpers import scored_opportunity as _opportunity


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
