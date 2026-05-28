from wraeclast_quant.commands.status_health_calibration_rows import (
    calibration_prompt_details,
    calibration_prompt_status,
)
from wraeclast_quant.commands.status_health_context_model import StatusHealthContext
from wraeclast_quant.storage.models import AnalysisRunRecord, ReviewCoverageRecord


def _context(
    *,
    latest: AnalysisRunRecord | None,
    coverage: ReviewCoverageRecord | None,
    calibration_prompts: list[str],
) -> StatusHealthContext:
    return StatusHealthContext(
        resources=[],
        assessments=[],
        eligible_count=0,
        backups=[],
        database_health=None,
        database_exists=latest is not None,
        latest=latest,
        latest_run_id=latest.id if latest is not None else None,
        coverage=coverage,
        calibration_prompts=calibration_prompts,
        market_brief_health=None,
        intel_validation=None,
        intel_error="",
        static_site_health=None,
        site_bundle_health=None,
        stash_ninja_health=None,
    )


def test_calibration_prompt_row_points_reviewed_prompts_to_calibration() -> None:
    context = _context(
        latest=AnalysisRunRecord(
            id=13,
            created_at="2026-05-28T02:16:42+00:00",
            source_mode="manual-import",
            item_count=6,
        ),
        coverage=ReviewCoverageRecord(
            run_id=13,
            total_recommendations=6,
            reviewed_recommendations=6,
            unreviewed_recommendations=0,
            reviewed_percent=100.0,
        ),
        calibration_prompts=["AVOID has positive outcomes.", "Positive average is low."],
    )

    assert calibration_prompt_status(context) == "ok"
    details = calibration_prompt_details(context)
    assert "2 local read-only prompt(s)" in details
    assert "wq calibration" in details
    assert "do not retune scoring or change recommendations" in details


def test_calibration_prompt_row_is_empty_before_local_runs() -> None:
    context = _context(latest=None, coverage=None, calibration_prompts=[])

    assert calibration_prompt_status(context) == "none"
    assert "No local run yet" in calibration_prompt_details(context)


def test_calibration_prompt_row_reports_no_prompts_without_failing_status() -> None:
    context = _context(
        latest=AnalysisRunRecord(
            id=7,
            created_at="2026-05-24T00:00:00+00:00",
            source_mode="manual-import",
            item_count=2,
        ),
        coverage=ReviewCoverageRecord(
            run_id=7,
            total_recommendations=2,
            reviewed_recommendations=2,
            unreviewed_recommendations=0,
            reviewed_percent=100.0,
        ),
        calibration_prompts=[],
    )

    assert calibration_prompt_status(context) == "ok"
    assert "No calibration review prompts triggered" in calibration_prompt_details(context)
