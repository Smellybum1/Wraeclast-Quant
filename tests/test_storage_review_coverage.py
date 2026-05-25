from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.repositories import SnapshotRepository


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
