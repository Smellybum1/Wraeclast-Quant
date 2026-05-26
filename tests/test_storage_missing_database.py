from pathlib import Path

from wraeclast_quant.storage.repositories import SnapshotRepository


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
