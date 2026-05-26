from pathlib import Path

from wraeclast_quant.reports.publish_check import check_publish_readiness

from site_bundle_helpers import write_publish_ready_bundle as _write_publish_ready_bundle


def test_publish_check_reports_invalid_public_intel(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "public_intel.json").write_text("{}", encoding="utf-8")

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is False
    assert any("Public intel contract" in blocker for blocker in result.blockers)


def test_publish_check_reports_invalid_archive(tmp_path: Path) -> None:
    database_path, bundle_dir, _run_id = _write_publish_ready_bundle(tmp_path)
    (bundle_dir / "wraeclast_quant_site_bundle.zip").write_bytes(b"not a zip")

    result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)

    assert result.ready is False
    assert any("not a valid zip file" in blocker for blocker in result.blockers)
