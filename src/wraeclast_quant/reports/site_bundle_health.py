from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from wraeclast_quant.reports.site_bundle_manifest import manifest_errors
from wraeclast_quant.reports.site_bundle_models import (
    ARCHIVE_NAME,
    DEFAULT_SITE_BUNDLE_DIR,
    REQUIRED_ARCHIVE_MEMBERS,
    SiteBundleHealthResult,
)


def check_site_bundle_health(bundle_dir: Path = DEFAULT_SITE_BUNDLE_DIR) -> SiteBundleHealthResult | None:
    archive_path = bundle_dir / ARCHIVE_NAME
    manifest_path = bundle_dir / "manifest.json"
    if not archive_path.exists():
        return None

    errors: list[str] = []
    manifest: dict[str, Any] = {}
    if not manifest_path.exists():
        errors.append("manifest.json is missing")
    else:
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"manifest.json is invalid JSON: {error.msg}")
        else:
            if not isinstance(loaded, dict):
                errors.append("manifest.json must be a JSON object")
            else:
                manifest = loaded
                errors.extend(manifest_errors(manifest))

    try:
        with zipfile.ZipFile(archive_path) as archive:
            members = set(archive.namelist())
    except zipfile.BadZipFile:
        members = set()
        errors.append("bundle archive is not a valid zip file")

    missing_members = sorted(REQUIRED_ARCHIVE_MEMBERS - members)
    if missing_members:
        errors.append("archive is missing: " + ", ".join(missing_members))

    return SiteBundleHealthResult(
        bundle_dir=bundle_dir,
        archive_path=archive_path,
        manifest_path=manifest_path,
        valid=not errors,
        errors=errors,
        schema_version=str(manifest.get("public_intel_schema_version", "")),
        latest_run_id=_optional_int(manifest.get("public_intel_latest_run_id")),
        top_opportunities_count=_optional_int(
            manifest.get("public_intel_top_opportunities")
        ),
        alerts_count=_optional_int(manifest.get("public_intel_alerts")),
        archive_size_bytes=archive_path.stat().st_size,
    )


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
