from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.public_intel_contract import PublicIntelValidationResult
from wraeclast_quant.reports.site_bundle_manifest_validation import manifest_errors


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

__all__ = ["manifest_errors", "site_bundle_manifest"]
