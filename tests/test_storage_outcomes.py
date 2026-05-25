from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_save_and_list_recommendation_outcomes(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)

    outcome = repository.save_recommendation_outcome(
        run_id=run.id,
        item_name="Stormglass Catalyst",
        outcome="positive",
        notes="Worked as expected.",
    )

    stored = repository.list_recent_outcomes()
    assert outcome.id == stored[0].id
    assert stored[0].run_id == run.id
    assert stored[0].item_name == "Stormglass Catalyst"
    assert stored[0].outcome == "positive"
    assert stored[0].notes == "Worked as expected."


def test_recommendation_outcome_summary_counts_outcomes(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)

    repository.save_recommendation_outcome(run.id, opportunities[0].item_name, "positive")
    repository.save_recommendation_outcome(run.id, opportunities[1].item_name, "negative")

    assert repository.outcome_summary() == {
        "negative": 1,
        "neutral": 0,
        "positive": 1,
    }


def test_outcome_reviews_include_original_score_and_action(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    repository.save_recommendation_outcome(
        run.id,
        opportunities[0].item_name,
        "positive",
        notes="Manual review.",
    )

    reviews = repository.list_outcome_reviews()

    assert len(reviews) == 1
    assert reviews[0].item_name == opportunities[0].item_name
    assert reviews[0].opportunity_score == opportunities[0].opportunity_score
    assert reviews[0].action == opportunities[0].action
    assert reviews[0].outcome == "positive"
    assert reviews[0].notes == "Manual review."


def test_outcome_reviews_can_fetch_all_without_limit(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    repository.save_recommendation_outcome(run.id, opportunities[0].item_name, "positive")
    repository.save_recommendation_outcome(run.id, opportunities[1].item_name, "neutral")
    repository.save_recommendation_outcome(run.id, opportunities[2].item_name, "negative")

    limited = repository.list_outcome_reviews(limit=2)
    all_reviews = repository.list_outcome_reviews(limit=None)

    assert len(limited) == 2
    assert len(all_reviews) == 3


def test_unreviewed_opportunities_excludes_items_with_outcomes(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    repository.save_recommendation_outcome(run.id, opportunities[0].item_name, "positive")

    unreviewed = repository.unreviewed_opportunities_for_run(run.id)

    assert opportunities[0].item_name not in [record.item_name for record in unreviewed]
    assert len(unreviewed) == len(opportunities) - 1
    assert unreviewed[0].opportunity_score >= unreviewed[-1].opportunity_score


def test_unreviewed_opportunities_respects_limit(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)

    unreviewed = repository.unreviewed_opportunities_for_run(run.id, limit=2)

    assert len(unreviewed) == 2


def test_review_coverage_counts_reviewed_and_unreviewed_items(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    repository.save_recommendation_outcome(run.id, opportunities[0].item_name, "positive")
    repository.save_recommendation_outcome(run.id, opportunities[0].item_name, "neutral")
    repository.save_recommendation_outcome(run.id, opportunities[1].item_name, "negative")

    coverage = repository.review_coverage_for_run(run.id)

    assert coverage.run_id == run.id
    assert coverage.total_recommendations == len(opportunities)
    assert coverage.reviewed_recommendations == 2
    assert coverage.unreviewed_recommendations == len(opportunities) - 2
    assert coverage.reviewed_percent == 20.0


def test_review_coverage_handles_empty_run(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    run = repository.create_analysis_run(source_mode="sample-data", item_count=0)

    coverage = repository.review_coverage_for_run(run.id)

    assert coverage.total_recommendations == 0
    assert coverage.reviewed_recommendations == 0
    assert coverage.unreviewed_recommendations == 0
    assert coverage.reviewed_percent == 0.0


def test_outcome_review_summary_groups_by_action_and_outcome(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))
    repository.save_scored_opportunities(run.id, opportunities)
    repository.save_recommendation_outcome(run.id, opportunities[0].item_name, "positive")
    repository.save_recommendation_outcome(run.id, opportunities[1].item_name, "negative")

    summary = repository.outcome_review_summary_by_action()

    assert summary[opportunities[0].action]["positive"] == 1
    assert summary[opportunities[0].action]["neutral"] == 0
    assert summary[opportunities[1].action]["negative"] == 1


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
