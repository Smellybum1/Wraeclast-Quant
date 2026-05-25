import zipfile
from pathlib import Path

from wraeclast_quant.reports.site_bundle import check_site_bundle_health, write_site_bundle

from site_bundle_helpers import write_inputs as _write_inputs


def test_check_site_bundle_health_reports_manifest_metadata(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"
    write_site_bundle(intel_path=intel_path, site_dir=site_dir, output_dir=output_dir)

    health = check_site_bundle_health(output_dir)

    assert health is not None
    assert health.valid is True
    assert health.errors == []
    assert health.schema_version == "1.0"
    assert health.latest_run_id == 7
    assert health.top_opportunities_count == 0
    assert health.alerts_count == 0
    assert health.archive_size_bytes > 0


def test_check_site_bundle_health_reports_missing_manifest(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    archive_path = bundle_dir / "wraeclast_quant_site_bundle.zip"
    with zipfile.ZipFile(archive_path, mode="w") as archive:
        archive.writestr("index.html", "<h1>Wraeclast Quant</h1>")

    health = check_site_bundle_health(bundle_dir)

    assert health is not None
    assert health.valid is False
    assert "manifest.json is missing" in health.errors
    assert "archive is missing: manifest.json, public_intel.json" in health.errors


def test_check_site_bundle_health_missing_archive_returns_none(tmp_path: Path) -> None:
    assert check_site_bundle_health(tmp_path / "missing") is None
