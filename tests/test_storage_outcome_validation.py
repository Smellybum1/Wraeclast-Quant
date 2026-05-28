from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_recommendation_outcome_rejects_invalid_run_or_item(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)

    try:
        repository.save_recommendation_outcome(999, "Stormglass Catalyst", "positive")
    except ValueError as error:
        assert "analysis run #999 was not found" in str(error)
    else:
        raise AssertionError("Expected missing run to be rejected")

    try:
        repository.save_recommendation_outcome(run.id, "Missing Item", "positive")
    except ValueError as error:
        assert "Missing Item" in str(error)
    else:
        raise AssertionError("Expected missing item to be rejected")


def test_recommendation_outcome_rejects_invalid_outcome(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)

    try:
        repository.save_recommendation_outcome(run.id, "Stormglass Catalyst", "great")
    except ValueError as error:
        assert "outcome must be one of" in str(error)
    else:
        raise AssertionError("Expected invalid outcome to be rejected")


def test_recommendation_outcome_rejects_duplicate_run_item(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)

    repository.save_recommendation_outcome(run.id, "Stormglass Catalyst", "positive")

    try:
        repository.save_recommendation_outcome(run.id, "stormglass catalyst", "neutral")
    except ValueError as error:
        assert "already has a recorded outcome" in str(error)
    else:
        raise AssertionError("Expected duplicate outcome to be rejected")

    records = repository.list_recent_outcomes()
    assert len(records) == 1
    assert records[0].outcome == "positive"
