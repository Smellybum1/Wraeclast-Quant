from __future__ import annotations

from pathlib import Path

from wraeclast_quant.commands.status_health_freshness import fresh_artifact_details
from wraeclast_quant.reports.public_intel_contract import PublicIntelValidationResult


def public_intel_status(
    path: Path,
    validation: PublicIntelValidationResult | None,
    error: str,
) -> str:
    if not path.exists():
        return "no"
    if error or validation is None or not validation.valid:
        return "needs attention"
    return "ok"


def public_intel_details(
    path: Path,
    validation: PublicIntelValidationResult | None,
    error: str,
    latest_database_run_id: int | None,
) -> str:
    if not path.exists():
        return str(path)
    if error:
        return f"{path}; {error}"
    if validation is None:
        return f"{path}; validation did not run"
    if not validation.valid:
        return f"{path}; " + "; ".join(validation.errors)
    details = (
        f"{path}; schema {validation.schema_version}; "
        f"latest run #{validation.latest_run_id or 'none'}; "
        f"{validation.top_opportunities_count} opportunities; "
        f"{validation.alerts_count} alerts"
    )
    return details + fresh_artifact_details(
        artifact_run_id=validation.latest_run_id,
        latest_database_run_id=latest_database_run_id,
        artifact_label="artifact",
        guidance="run wq export and wq site",
    )


def public_intel_run_id(validation: PublicIntelValidationResult | None) -> int | None:
    return validation.latest_run_id if validation is not None and validation.valid else None
