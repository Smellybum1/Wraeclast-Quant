from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import ConnectorReviewStatusRow


def evidence_status_row(
    check: str,
    value: str,
    related_review_complete: bool,
) -> ConnectorReviewStatusRow:
    normalized = value.strip()
    if normalized:
        status = "ok"
    elif related_review_complete:
        status = "blocked"
    else:
        status = "needs-review"
    return ConnectorReviewStatusRow(
        check=check,
        value=normalized or "",
        status=status,
    )


def optional_status_row(check: str, value: str) -> ConnectorReviewStatusRow:
    normalized = value.strip()
    return ConnectorReviewStatusRow(
        check=check,
        value=normalized or "",
        status="ok" if normalized else "optional",
    )


def required_when_complete_status_row(
    check: str,
    value: str,
    review_complete: bool,
) -> ConnectorReviewStatusRow:
    normalized = value.strip()
    if normalized:
        status = "ok"
    elif review_complete:
        status = "blocked"
    else:
        status = "optional"
    return ConnectorReviewStatusRow(
        check=check,
        value=normalized or "",
        status=status,
    )


__all__ = [
    "evidence_status_row",
    "optional_status_row",
    "required_when_complete_status_row",
]
