from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    PublicIntelValidationResult,
    validate_public_intel_file,
)


def load_public_intel_validation(
    intel_path: Path,
) -> tuple[PublicIntelValidationResult | None, str]:
    if not intel_path.exists():
        return None, ""

    try:
        return validate_public_intel_file(intel_path), ""
    except PublicIntelContractError as error:
        return None, str(error)


__all__ = ["load_public_intel_validation"]
