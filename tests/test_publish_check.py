from pathlib import Path

from wraeclast_quant.reports.publish_check import (
    check_publish_readiness,
    publish_check_payload,
)

from site_bundle_helpers import write_publish_ready_bundle as _write_publish_ready_bundle


def test_publish_check_ready_for_fresh_valid_bundle(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is True
    assert result.latest_database_run_id == run_id
    assert result.bundle_latest_run_id == run_id
    assert result.blockers == []
    assert result.files == ["index.html", "manifest.json", "public_intel.json"]
    assert {row.key: row.status for row in result.checks}["manual_publish_readiness"] == "ready"


def test_publish_check_reports_stale_bundle(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(
        tmp_path,
        artifact_run_id=1,
        database_runs=2,
    )

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is False
    assert result.latest_database_run_id == 2
    assert result.bundle_latest_run_id == 1
    assert any("latest database run #2, bundle run #1" in blocker for blocker in result.blockers)


def test_publish_check_missing_bundle_is_non_mutating(tmp_path: Path) -> None:
    database_path, _bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    missing_dir = tmp_path / "missing_bundle"

    result = check_publish_readiness(database_path=database_path, bundle_dir=missing_dir)

    assert result.ready is False
    assert any("not found" in blocker for blocker in result.blockers)
    assert not missing_dir.exists()


def test_publish_check_json_payload_has_stable_keys(tmp_path: Path) -> None:
    database_path, bundle_dir, run_id = _write_publish_ready_bundle(tmp_path)

    payload = publish_check_payload(check_publish_readiness(database_path, bundle_dir))

    assert payload["ready"] is True
    assert payload["latest_database_run_id"] == run_id
    assert payload["bundle_latest_run_id"] == run_id
    assert isinstance(payload["checks"], list)
    assert payload["blockers"] == []
