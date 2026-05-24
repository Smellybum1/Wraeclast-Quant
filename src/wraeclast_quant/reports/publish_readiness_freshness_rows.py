from __future__ import annotations

from wraeclast_quant.reports.publish_models import PublishCheckRow
from wraeclast_quant.reports.publish_readiness_blocking_rows import add_blocking_check


def add_freshness_check(
    checks: list[PublishCheckRow],
    blockers: list[str],
    key: str,
    check: str,
    artifact_label: str,
    artifact_run_id: int | None,
    latest_database_run_id: int | None,
) -> None:
    if latest_database_run_id is None or artifact_run_id is None:
        add_blocking_check(
            checks,
            blockers,
            key,
            check,
            "unknown",
            f"Could not compare {artifact_label} run id to latest database run.",
        )
        return
    if artifact_run_id != latest_database_run_id:
        add_blocking_check(
            checks,
            blockers,
            key,
            check,
            "stale",
            (
                f"stale; latest database run #{latest_database_run_id}, "
                f"{artifact_label} run #{artifact_run_id}"
            ),
        )
        return
    checks.append(
        PublishCheckRow(
            key=key,
            check=check,
            status="ok",
            details=f"latest database run #{latest_database_run_id}; {artifact_label} run #{artifact_run_id}",
        )
    )


__all__ = ["add_freshness_check"]
