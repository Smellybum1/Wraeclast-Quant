from wraeclast_quant.commands.status_health_context_model import StatusHealthContext
from wraeclast_quant.commands.status_health_mvp_rows import mvp_readiness_details
from wraeclast_quant.storage.models import AnalysisRunRecord, ReviewCoverageRecord


def test_mvp_readiness_points_fully_reviewed_runs_to_manual_snapshot_loop() -> None:
    context = StatusHealthContext(
        resources=[],
        assessments=[],
        eligible_count=0,
        backups=[],
        database_health=None,
        database_exists=True,
        latest=AnalysisRunRecord(
            id=7,
            created_at="2026-05-24T00:00:00+00:00",
            source_mode="manual-import",
            item_count=2,
        ),
        latest_run_id=7,
        coverage=ReviewCoverageRecord(
            run_id=7,
            total_recommendations=2,
            reviewed_recommendations=2,
            unreviewed_recommendations=0,
            reviewed_percent=100.0,
        ),
        market_brief_health=None,
        intel_validation=None,
        intel_error="",
        static_site_health=None,
        site_bundle_health=None,
        stash_ninja_health=None,
    )

    details = mvp_readiness_details(context)

    assert "2/2 reviewed" in details
    assert "wq currency-exchange-manual-snapshot --input-path <current-snapshot>" in details
    assert "docs/MVP_DAILY_WORKFLOW.md" in details
    assert "wq daily --input-path <manual-import-output>" in details


def test_mvp_readiness_points_unreviewed_runs_to_batch_dry_run_loop() -> None:
    context = StatusHealthContext(
        resources=[],
        assessments=[],
        eligible_count=0,
        backups=[],
        database_health=None,
        database_exists=True,
        latest=AnalysisRunRecord(
            id=7,
            created_at="2026-05-24T00:00:00+00:00",
            source_mode="manual-import",
            item_count=2,
        ),
        latest_run_id=7,
        coverage=ReviewCoverageRecord(
            run_id=7,
            total_recommendations=2,
            reviewed_recommendations=1,
            unreviewed_recommendations=1,
            reviewed_percent=50.0,
        ),
        market_brief_health=None,
        intel_validation=None,
        intel_error="",
        static_site_health=None,
        site_bundle_health=None,
        stash_ninja_health=None,
    )

    details = mvp_readiness_details(context)

    assert "1/2 reviewed" in details
    assert "wq review-coverage --run-id 7" in details
    assert "worksheet, outcome-decisions, and dry-run steps" in details


def test_mvp_readiness_points_empty_state_to_manual_snapshot_loop() -> None:
    context = StatusHealthContext(
        resources=[],
        assessments=[],
        eligible_count=0,
        backups=[],
        database_health=None,
        database_exists=False,
        latest=None,
        latest_run_id=None,
        coverage=None,
        market_brief_health=None,
        intel_validation=None,
        intel_error="",
        static_site_health=None,
        site_bundle_health=None,
        stash_ninja_health=None,
    )

    details = mvp_readiness_details(context)

    assert details.startswith("No local run yet")
    assert "wq currency-exchange-manual-snapshot --input-path <current-snapshot>" in details
    assert "wq daily --input-path <manual-import-output>" in details
