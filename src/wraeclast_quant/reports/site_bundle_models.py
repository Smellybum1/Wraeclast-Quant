from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

DEFAULT_SITE_BUNDLE_DIR = Path("data/processed/site_bundle")
ARCHIVE_NAME = "wraeclast_quant_site_bundle.zip"
REQUIRED_MANIFEST_KEYS = {
    "generated_at",
    "product",
    "bundle_type",
    "derived_only",
    "network_behavior",
    "public_intel_schema_version",
    "public_intel_latest_run_id",
    "public_intel_top_opportunities",
    "public_intel_alerts",
    "files",
    "safety",
}
REQUIRED_ARCHIVE_MEMBERS = {"index.html", "manifest.json", "public_intel.json"}


class SiteBundleError(ValueError):
    pass


class SiteBundleResult(BaseModel):
    bundle_dir: Path
    archive_path: Path
    files: list[str]
    generated_at: str


@dataclass(frozen=True)
class SiteBundleHealthResult:
    bundle_dir: Path
    archive_path: Path
    manifest_path: Path
    valid: bool
    errors: list[str]
    schema_version: str
    latest_run_id: int | None
    top_opportunities_count: int | None
    alerts_count: int | None
    archive_size_bytes: int
