from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.repositories import SnapshotRepository


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
