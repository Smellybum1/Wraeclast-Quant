from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def run_payload(run: AnalysisRunRecord) -> dict[str, Any]:
    return {
        "id": run.id,
        "created_at": run.created_at,
        "source_mode": run.source_mode,
        "item_count": run.item_count,
    }


def opportunity_payload(opportunity: StoredOpportunityRecord) -> dict[str, Any]:
    return {
        "item_name": opportunity.item_name,
        "opportunity_score": opportunity.opportunity_score,
        "action": opportunity.action,
    }
