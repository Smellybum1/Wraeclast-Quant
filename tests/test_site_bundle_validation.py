import json
from pathlib import Path

import pytest

from wraeclast_quant.reports.site_bundle import (
    SiteBundleError,
    write_site_bundle,
)

from site_bundle_helpers import public_intel_payload as _public_intel_payload


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
