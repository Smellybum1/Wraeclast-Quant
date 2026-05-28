from pathlib import Path

from wraeclast_quant.reports.publish_check import (
    check_publish_readiness,
    write_publish_handoff,
)

from site_bundle_helpers import write_publish_ready_bundle as _write_publish_ready_bundle


def test_publish_handoff_missing_bundle_does_not_create_bundle(tmp_path: Path) -> None:
    database_path, _bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    missing_dir = tmp_path / "missing_bundle"
    output_path = tmp_path / "publish_handoff.md"
    result = check_publish_readiness(database_path, missing_dir)

    write_publish_handoff(result, output_path)

    assert output_path.exists()
    assert not missing_dir.exists()
    assert "not found" in output_path.read_text(encoding="utf-8")


def test_publish_handoff_excludes_raw_inputs_and_sensitive_values(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    result = check_publish_readiness(database_path, bundle_dir)
    output_path = tmp_path / "publish_handoff.md"

    write_publish_handoff(result, output_path)

    report = output_path.read_text(encoding="utf-8")
    forbidden = [
        "raw signal inputs",
        "resource notes:",
        "RESOURCES.md content",
        "secret-token-value",
        "cookie=",
        "api_key=",
        "Stormglass Catalyst inputs",
    ]
    for value in forbidden:
        assert value not in report


def test_publish_handoff_names_local_feedback_artifacts_as_excluded(
    tmp_path: Path,
) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    result = check_publish_readiness(database_path, bundle_dir)
    output_path = tmp_path / "publish_handoff.md"

    write_publish_handoff(result, output_path)

    report = output_path.read_text(encoding="utf-8")
    assert "`review_queue*.md`" in report
    assert "`outcome_decisions*.json`" in report
    assert "`outcome_review.md`" in report
    assert "`calibration_report.md`" in report
    assert "`exile_ui_stash_ninja_watchlist.*`" in report
    assert "not public handoff inputs" in report
