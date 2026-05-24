from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    PublicIntelValidationResult,
    validate_public_intel_file,
)
from wraeclast_quant.reports.site_bundle_models import SiteBundleError


def validate_site_bundle_inputs(
    intel_path: Path,
    index_path: Path,
) -> PublicIntelValidationResult:
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
    return validation


__all__ = ["validate_site_bundle_inputs"]
