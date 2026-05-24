from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.site_bundle_health_archive import archive_member_errors
from wraeclast_quant.reports.site_bundle_health_manifest import (
    load_health_manifest,
    optional_int,
)
from wraeclast_quant.reports.site_bundle_models import (
    ARCHIVE_NAME,
    DEFAULT_SITE_BUNDLE_DIR,
    SiteBundleHealthResult,
)


def check_site_bundle_health(bundle_dir: Path = DEFAULT_SITE_BUNDLE_DIR) -> SiteBundleHealthResult | None:
    archive_path = bundle_dir / ARCHIVE_NAME
    manifest_path = bundle_dir / "manifest.json"
    if not archive_path.exists():
        return None

    manifest, errors = load_health_manifest(manifest_path)
    errors.extend(archive_member_errors(archive_path))

    return SiteBundleHealthResult(
        bundle_dir=bundle_dir,
        archive_path=archive_path,
        manifest_path=manifest_path,
        valid=not errors,
        errors=errors,
        schema_version=str(manifest.get("public_intel_schema_version", "")),
        latest_run_id=optional_int(manifest.get("public_intel_latest_run_id")),
        top_opportunities_count=optional_int(
            manifest.get("public_intel_top_opportunities")
        ),
        alerts_count=optional_int(manifest.get("public_intel_alerts")),
        archive_size_bytes=archive_path.stat().st_size,
    )


__all__ = ["check_site_bundle_health"]
