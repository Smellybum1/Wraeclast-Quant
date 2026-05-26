import json
import zipfile
from pathlib import Path

import pytest

from wraeclast_quant.reports.site_bundle import (
    SiteBundleError,
    write_site_bundle,
)

from site_bundle_helpers import public_intel_payload as _public_intel_payload
from site_bundle_helpers import write_inputs as _write_inputs


def test_write_site_bundle_copies_derived_artifacts_and_manifest(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"

    result = write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    assert result.bundle_dir == output_dir
    assert (output_dir / "index.html").read_text(encoding="utf-8") == "<h1>Wraeclast Quant</h1>"
    assert json.loads((output_dir / "public_intel.json").read_text(encoding="utf-8"))[
        "latest_run"
    ]["id"] == 7
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["product"] == "Wraeclast Quant"
    assert manifest["derived_only"] is True
    assert manifest["network_behavior"] == "none"
    assert manifest["public_intel_schema_version"] == "1.0"
    assert manifest["public_intel_latest_run_id"] == 7
    assert manifest["public_intel_top_opportunities"] == 0
    assert manifest["public_intel_alerts"] == 0


def test_write_site_bundle_creates_zip_with_expected_files(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"

    result = write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    assert result.archive_path == output_dir / "wraeclast_quant_site_bundle.zip"
    with zipfile.ZipFile(result.archive_path) as archive:
        assert sorted(archive.namelist()) == [
            "index.html",
            "manifest.json",
            "public_intel.json",
        ]


def test_write_site_bundle_rejects_missing_public_intel(tmp_path: Path) -> None:
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")

    with pytest.raises(SiteBundleError, match="No public intel export found"):
        write_site_bundle(
            intel_path=tmp_path / "missing.json",
            site_dir=site_dir,
            output_dir=tmp_path / "bundle",
        )


def test_write_site_bundle_rejects_missing_static_site(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    intel_path.write_text(json.dumps(_public_intel_payload()), encoding="utf-8")

    with pytest.raises(SiteBundleError, match="No static site found"):
        write_site_bundle(
            intel_path=intel_path,
            site_dir=tmp_path / "missing_site",
            output_dir=tmp_path / "bundle",
        )


def test_write_site_bundle_rejects_invalid_public_intel(tmp_path: Path) -> None:
    intel_path = tmp_path / "public_intel.json"
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    intel_path.write_text(json.dumps({"latest_run": {"id": 7}}), encoding="utf-8")
    (site_dir / "index.html").write_text("<h1>Wraeclast Quant</h1>", encoding="utf-8")

    with pytest.raises(SiteBundleError, match="Public intel contract validation failed"):
        write_site_bundle(
            intel_path=intel_path,
            site_dir=site_dir,
            output_dir=tmp_path / "bundle",
        )


def test_site_bundle_manifest_excludes_source_paths_and_secrets(tmp_path: Path) -> None:
    intel_path, site_dir = _write_inputs(tmp_path)
    output_dir = tmp_path / "bundle"

    write_site_bundle(
        intel_path=intel_path,
        site_dir=site_dir,
        output_dir=output_dir,
    )

    manifest_text = (output_dir / "manifest.json").read_text(encoding="utf-8")
    assert str(tmp_path) not in manifest_text
    assert "secret-token-value" not in manifest_text
    assert ".env" in manifest_text
