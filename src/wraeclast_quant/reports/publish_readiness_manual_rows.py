from __future__ import annotations

from wraeclast_quant.reports.publish_models import PublishCheckRow


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


__all__ = ["add_manual_publish_readiness"]
