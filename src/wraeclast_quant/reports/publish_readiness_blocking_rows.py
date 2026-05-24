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


__all__ = ["add_blocking_check"]
