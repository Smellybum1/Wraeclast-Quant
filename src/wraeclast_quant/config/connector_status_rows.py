from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import ConnectorReviewStatusRow


def boolean_status_row(check: str, value: bool) -> ConnectorReviewStatusRow:
    return ConnectorReviewStatusRow(
        check=check,
        value="yes" if value else "no",
        status="ok" if value else "needs-review",
    )


def inverse_boolean_status_row(check: str, value: bool) -> ConnectorReviewStatusRow:
    return ConnectorReviewStatusRow(
        check=check,
        value="yes" if value else "no",
        status="blocked" if value else "ok",
    )


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
