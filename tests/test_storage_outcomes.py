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
