from __future__ import annotations

from wraeclast_quant.intelligence.snapshot_delta_models import OpportunityDelta
from wraeclast_quant.storage.models import StoredOpportunityRecord


def records_by_item_name(
    records: list[StoredOpportunityRecord],
) -> dict[str, StoredOpportunityRecord]:
    return {record.item_name: record for record in records}


def compared_item_names(
    previous_by_name: dict[str, StoredOpportunityRecord],
    latest_by_name: dict[str, StoredOpportunityRecord],
) -> list[str]:
    return sorted(set(previous_by_name) | set(latest_by_name))


def new_item_delta(item_name: str, latest_record: StoredOpportunityRecord) -> OpportunityDelta:
    return OpportunityDelta(
        item_name=item_name,
        status="new",
        latest_score=latest_record.opportunity_score,
        latest_action=latest_record.action,
    )


def removed_item_delta(
    item_name: str,
    previous_record: StoredOpportunityRecord,
) -> OpportunityDelta:
    return OpportunityDelta(
        item_name=item_name,
        status="removed",
        previous_score=previous_record.opportunity_score,
        previous_action=previous_record.action,
    )


def changed_item_delta(
    item_name: str,
    previous_record: StoredOpportunityRecord,
    latest_record: StoredOpportunityRecord,
) -> OpportunityDelta:
    score_delta = round(
        latest_record.opportunity_score - previous_record.opportunity_score,
        2,
    )
    return OpportunityDelta(
        item_name=item_name,
        status="changed",
        previous_score=previous_record.opportunity_score,
        latest_score=latest_record.opportunity_score,
        score_delta=score_delta,
        previous_action=previous_record.action,
        latest_action=latest_record.action,
        action_changed=previous_record.action != latest_record.action,
    )


__all__ = [
    "changed_item_delta",
    "compared_item_names",
    "new_item_delta",
    "records_by_item_name",
    "removed_item_delta",
]
