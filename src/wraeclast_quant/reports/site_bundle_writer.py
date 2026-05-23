from __future__ import annotations

import json
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.site_bundle_manifest import site_bundle_manifest
from wraeclast_quant.reports.site_bundle_models import (
    ARCHIVE_NAME,
    DEFAULT_SITE_BUNDLE_DIR,
    SiteBundleError,
    SiteBundleResult,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR


def write_site_bundle(
    intel_path: Path = DEFAULT_PUBLIC_INTEL_PATH,
    site_dir: Path = DEFAULT_SITE_DIR,
    output_dir: Path = DEFAULT_SITE_BUNDLE_DIR,
) -> SiteBundleResult:
    index_path = site_dir / "index.html"
    if not intel_path.exists():
        raise SiteBundleError("No public intel export found. Run wq export first.")
    if not index_path.exists():
        raise SiteBundleError("No static site found. Run wq site first.")
    try:
        validation = validate_public_intel_file(intel_path)
    except PublicIntelContractError as error:
        raise SiteBundleError(str(error)) from error
    if not validation.valid:
        raise SiteBundleError(
            "Public intel contract validation failed: " + "; ".join(validation.errors)
        )

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
