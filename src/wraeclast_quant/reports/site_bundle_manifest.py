from __future__ import annotations

from pathlib import Path
from typing import Any

from wraeclast_quant.reports.public_intel_contract import PublicIntelValidationResult
from wraeclast_quant.reports.site_bundle_models import REQUIRED_MANIFEST_KEYS


def site_bundle_manifest(
    generated_at: str,
    files: list[Path],
    validation: PublicIntelValidationResult,
) -> dict[str, object]:
    return {
        "generated_at": generated_at,
        "product": "Wraeclast Quant",
        "bundle_type": "local-static-preview",
        "derived_only": True,
        "network_behavior": "none",
        "public_intel_schema_version": validation.schema_version,
        "public_intel_latest_run_id": validation.latest_run_id,
        "public_intel_top_opportunities": validation.top_opportunities_count,
        "public_intel_alerts": validation.alerts_count,
        "files": [
            {
                "path": path.name,
                "size_bytes": path.stat().st_size,
            }
            for path in files
        ],
        "safety": (
            "Contains derived local public-intel artifacts only. "
            "No raw source data, credentials, cookies, tokens, or .env values are included."
        ),
    }


def manifest_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_MANIFEST_KEYS - set(manifest))
    if missing:
        errors.append("manifest is missing: " + ", ".join(missing))
    if manifest.get("product") != "Wraeclast Quant":
        errors.append("manifest product must be Wraeclast Quant")
    if manifest.get("derived_only") is not True:
        errors.append("manifest derived_only must be true")
    if manifest.get("network_behavior") != "none":
        errors.append("manifest network_behavior must be none")
    if not isinstance(manifest.get("files"), list):
        errors.append("manifest files must be a list")
    return errors
