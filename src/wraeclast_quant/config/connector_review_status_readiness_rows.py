from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ConnectorCheckResult,
    ConnectorReviewStatusRow,
)


def readiness_status_row(result: ConnectorCheckResult) -> ConnectorReviewStatusRow:
    return ConnectorReviewStatusRow(
        check="Readiness",
        value="ready" if result.ready else "not ready",
        status="ok" if result.ready else "blocked",
    )
