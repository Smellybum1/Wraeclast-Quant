from __future__ import annotations

from typing import Any

from wraeclast_quant.reports.site_bundle_models import REQUIRED_MANIFEST_KEYS


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


__all__ = ["manifest_errors"]
