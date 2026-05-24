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


__all__ = ["boolean_status_row", "inverse_boolean_status_row"]
