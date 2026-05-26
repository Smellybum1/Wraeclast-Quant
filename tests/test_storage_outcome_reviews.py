from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.repositories import SnapshotRepository


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
