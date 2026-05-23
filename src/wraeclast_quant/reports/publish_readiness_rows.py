from __future__ import annotations

from wraeclast_quant.reports.publish_models import PublishCheckRow


def add_blocking_check(
    checks: list[PublishCheckRow],
    blockers: list[str],
    key: str,
    check: str,
    status: str,
    details: str,
) -> None:
    checks.append(
        PublishCheckRow(
            key=key,
            check=check,
            status=status,
            details=details,
        )
    )
    blockers.append(f"{check}: {details}")


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


def add_manual_publish_readiness(
    checks: list[PublishCheckRow],
    blockers: list[str],
) -> None:
    checks.append(
        PublishCheckRow(
            key="manual_publish_readiness",
            check="Manual publishing readiness",
            status="ready" if not blockers else "not ready",
            details="Ready for manual publishing." if not blockers else "Resolve blockers before publishing.",
        )
    )
