from pathlib import Path

from wraeclast_quant.storage.backups import verify_database_backup

from database_backup_helpers import sample_backup as _sample_backup


def test_verify_database_backup_reports_counts_and_latest_run(tmp_path: Path) -> None:
    backup, run, opportunities = _sample_backup(tmp_path)

    verification = verify_database_backup(backup.backup_path)

    assert verification.backup_path == backup.backup_path
    assert verification.schema_version == "2"
    assert verification.required_tables == [
        "analysis_runs",
        "recommendation_outcomes",
        "report_artifacts",
        "run_provenance",
        "scored_opportunities",
    ]
    assert verification.analysis_run_count == 1
    assert verification.scored_opportunity_count == len(opportunities)
    assert verification.report_artifact_count == 0
    assert verification.recommendation_outcome_count == 0
    assert verification.latest_run_id == run.id
    assert verification.latest_run_created_at == "2026-05-23T00:00:00+00:00"
    assert verification.latest_run_source_mode == "sample-data"
    assert verification.latest_run_item_count == len(opportunities)
