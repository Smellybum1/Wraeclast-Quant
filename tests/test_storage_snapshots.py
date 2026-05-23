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


def test_save_and_fetch_run_provenance(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    run = repository.create_analysis_run(source_mode="connector-fixture", item_count=2)

    saved = repository.save_run_provenance(
        run_id=run.id,
        source_kind="connector-fixture",
        resource_name="Example Approved API",
        connector_id="fixture-source-connector",
        access_method="api",
        metadata={
            "connector_class": "FixtureSourceConnector",
            "fixture_item_count": 2,
            "future_cache_path": "data/raw/cache/example.cache",
        },
    )
    fetched = repository.run_provenance(run.id)
    latest = repository.latest_run_provenance()

    assert saved.run_id == run.id
    assert fetched is not None
    assert fetched.resource_name == "Example Approved API"
    assert fetched.metadata["fixture_item_count"] == 2
    assert latest is not None
    assert latest.run_id == run.id


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


def test_save_report_artifact(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    run = repository.create_analysis_run(source_mode="sample-data", item_count=0)

    artifact = repository.save_report_artifact(run.id, Path("data/processed/market_brief.md"))

    assert artifact.run_id == run.id
    assert artifact.path == "data\\processed\\market_brief.md" or artifact.path == "data/processed/market_brief.md"
    assert artifact.created_at
    assert repository.report_artifacts_for_run(run.id)[0].id == artifact.id


def test_previous_run_before_fetches_prior_run(tmp_path: Path) -> None:
    repository = SnapshotRepository(tmp_path / "snapshots.db")
    first = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    second = repository.create_analysis_run(source_mode="sample-data", item_count=1)
    third = repository.create_analysis_run(source_mode="sample-data", item_count=1)

    previous = repository.previous_run_before(third.id)

    assert previous is not None
    assert previous.id == second.id
    assert repository.previous_run_before(first.id) is None


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
