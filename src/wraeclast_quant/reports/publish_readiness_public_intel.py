from __future__ import annotations

from pathlib import Path

from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_rows import add_blocking_check


def add_public_intel_checks(
    checks: list[PublishCheckRow],
    blockers: list[str],
    intel_path: Path,
) -> int | None:
    try:
        validation = validate_public_intel_file(intel_path)
    except PublicIntelContractError as error:
        add_blocking_check(
            checks,
            blockers,
            "public_intel_contract",
            "Public intel contract",
            "invalid",
            str(error),
        )
        return None
    if not validation.valid:
        add_blocking_check(
            checks,
            blockers,
            "public_intel_contract",
            "Public intel contract",
            "invalid",
            "; ".join(validation.errors),
        )
        return validation.latest_run_id
    checks.append(
        PublishCheckRow(
            key="public_intel_contract",
            check="Public intel contract",
            status="ok",
            details=(
                f"schema {validation.schema_version}; latest run "
                f"#{validation.latest_run_id or 'none'}"
            ),
        )
    )
    return validation.latest_run_id


__all__ = ["add_public_intel_checks"]
