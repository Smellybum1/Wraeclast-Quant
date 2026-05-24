from __future__ import annotations

from wraeclast_quant.intelligence.snapshot_delta_builders import (
    changed_item_delta,
    compared_item_names,
    new_item_delta,
    records_by_item_name,
    removed_item_delta,
)
from wraeclast_quant.intelligence.snapshot_delta_models import OpportunityDelta, SnapshotComparison
from wraeclast_quant.storage.models import StoredOpportunityRecord


def compare_opportunities(
    previous: list[StoredOpportunityRecord],
    latest: list[StoredOpportunityRecord],
    previous_run_id: int | None = None,
    latest_run_id: int | None = None,
) -> SnapshotComparison:
    previous_by_name = records_by_item_name(previous)
    latest_by_name = records_by_item_name(latest)
    deltas: list[OpportunityDelta] = []

    for item_name in compared_item_names(previous_by_name, latest_by_name):
        previous_record = previous_by_name.get(item_name)
        latest_record = latest_by_name.get(item_name)

        if previous_record is None and latest_record is not None:
            deltas.append(new_item_delta(item_name, latest_record))
            continue

        if latest_record is None and previous_record is not None:
            deltas.append(removed_item_delta(item_name, previous_record))
            continue

        if previous_record is None or latest_record is None:
            continue

        deltas.append(changed_item_delta(item_name, previous_record, latest_record))

    return SnapshotComparison(
        previous_run_id=previous_run_id,
        latest_run_id=latest_run_id,
        deltas=deltas,
    )


__all__ = ["compare_opportunities"]
