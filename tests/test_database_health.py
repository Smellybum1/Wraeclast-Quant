from pathlib import Path

from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.sample_data.items import SAMPLE_ITEMS
from wraeclast_quant.storage.health import check_database_health
from wraeclast_quant.storage.repositories import SnapshotRepository


def test_check_database_health_missing_database_returns_none_without_creating_it(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "missing" / "snapshots.db"

    assert check_database_health(database_path) is None
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_check_database_health_reports_counts_and_latest_run(tmp_path: Path) -> None:
    database_path = tmp_path / "snapshots.db"
    repository = SnapshotRepository(database_path)
    opportunities = rank_opportunities(SAMPLE_ITEMS)
    run = repository.create_analysis_run(
        source_mode="sample-data",
        item_count=len(opportunities),
        created_at="2026-05-23T00:00:00+00:00",
    )
    repository.save_scored_opportunities(run.id, opportunities)
    repository.save_report_artifact(run.id, Path("data/processed/market_brief.md"))
    repository.save_recommendation_outcome(run.id, opportunities[0].item_name, "positive")

    result = check_database_health(database_path)

    assert result is not None
    assert result.ok is True
    assert result.schema_version == "2"
    assert result.required_tables == [
        "analysis_runs",
        "recommendation_outcomes",
        "report_artifacts",
        "run_provenance",
        "scored_opportunities",
    ]
    assert result.integrity_ok is True
    assert result.integrity_message == "ok"
    assert result.schema_ok is True
    assert result.missing_tables == []
    assert result.analysis_run_count == 1
    assert result.scored_opportunity_count == len(opportunities)
    assert result.report_artifact_count == 1
    assert result.recommendation_outcome_count == 1
    assert result.latest_run_id == run.id
    assert result.latest_run_created_at == "2026-05-23T00:00:00+00:00"
    assert result.latest_run_source_mode == "sample-data"
    assert result.latest_run_item_count == len(opportunities)
