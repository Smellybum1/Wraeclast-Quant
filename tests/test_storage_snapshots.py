from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_schema_initialization_is_idempotent(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")

    repository.initialize_schema()
    repository.initialize_schema()

    assert repository.list_recent_runs() == []


def test_missing_database_reads_return_empty_without_creating_files(tmp_path: Path) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"
    repository = SnapshotRepository(database_path)

    assert repository.latest_run() is None
    assert repository.previous_run_before(1) is None
    assert repository.analysis_run(1) is None
    assert repository.list_recent_runs() == []
    assert repository.latest_scored_opportunities() == []
    assert repository.scored_opportunities_for_run(1) == []
    assert repository.unreviewed_opportunities_for_run(1) == []
    assert repository.report_artifacts_for_run(1) == []
    assert repository.run_provenance(1) is None
    assert repository.latest_run_provenance() is None
    assert repository.list_recent_outcomes() == []
    assert repository.outcome_summary() == {
        "negative": 0,
        "neutral": 0,
        "positive": 0,
    }
    assert repository.list_outcome_reviews() == []
    assert repository.outcome_review_summary_by_action() == {}

    coverage = repository.review_coverage_for_run(1)
    assert coverage.total_recommendations == 0
    assert coverage.reviewed_recommendations == 0
    assert coverage.unreviewed_recommendations == 0
    assert coverage.reviewed_percent == 0.0
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_save_and_fetch_scored_opportunities(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(source_mode="sample-data", item_count=len(opportunities))

    repository.save_scored_opportunities(run.id, opportunities)
    stored = repository.scored_opportunities_for_run(run.id)

    assert len(stored) == 10
    assert stored[0].item_name == "Stormglass Catalyst"
    assert stored[0].opportunity_score >= stored[-1].opportunity_score
    assert stored[0].inputs["demand_momentum"] == 88


def test_previous_run_before_fetches_prior_run(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    first = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    second = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    third = repository.create_analysis_run(source_mode="sample-data", item_count=1)

    previous = repository.previous_run_before(third.id)

    assert previous is not None
    assert previous.id == second.id
    assert repository.previous_run_before(first.id) is None
