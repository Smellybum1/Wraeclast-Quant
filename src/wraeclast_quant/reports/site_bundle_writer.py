from __future__ import annotations

import json
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.site_bundle_inputs import validate_site_bundle_inputs
from wraeclast_quant.reports.site_bundle_manifest import site_bundle_manifest
from wraeclast_quant.reports.site_bundle_models import (
    ARCHIVE_NAME,
    DEFAULT_SITE_BUNDLE_DIR,
    SiteBundleResult,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR


def write_site_bundle(
    intel_path: Path = DEFAULT_PUBLIC_INTEL_PATH,
    site_dir: Path = DEFAULT_SITE_DIR,
    output_dir: Path = DEFAULT_SITE_BUNDLE_DIR,
) -> SiteBundleResult:
    index_path = site_dir / "index.html"
    validation = validate_site_bundle_inputs(intel_path, index_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_index = output_dir / "index.html"
    bundle_intel = output_dir / "public_intel.json"
    manifest_path = output_dir / "manifest.json"
    archive_path = output_dir / ARCHIVE_NAME

    shutil.copyfile(index_path, bundle_index)
    shutil.copyfile(intel_path, bundle_intel)
    generated_at = datetime.now(UTC).isoformat()
    manifest = site_bundle_manifest(generated_at, [bundle_index, bundle_intel], validation)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    if archive_path.exists():
        archive_path.unlink()
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in [bundle_index, bundle_intel, manifest_path]:
            archive.write(path, arcname=path.name)

    return SiteBundleResult(
        bundle_dir=output_dir,
        archive_path=archive_path,
        files=["index.html", "public_intel.json", "manifest.json", ARCHIVE_NAME],
        generated_at=generated_at,
    )
