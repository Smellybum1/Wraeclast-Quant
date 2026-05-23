from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.storage.models import StoredOpportunityRecord


class OpportunityDelta(BaseModel):
    item_name: str
    status: str
    previous_score: float | None = None
    latest_score: float | None = None
    score_delta: float | None = None
    previous_action: str | None = None
    latest_action: str | None = None
    action_changed: bool = False


class SnapshotComparison(BaseModel):
    previous_run_id: int | None
    latest_run_id: int | None
    deltas: list[OpportunityDelta]

    @property
    def has_comparison(self) -> bool:
        return self.previous_run_id is not None and self.latest_run_id is not None

    @property
    def top_movers(self) -> list[OpportunityDelta]:
        return sorted(
            [
                delta
                for delta in self.deltas
                if delta.score_delta is not None and delta.score_delta != 0
            ],
            key=lambda delta: (-(abs(delta.score_delta or 0)), delta.item_name),
        )

    @property
    def status_changes(self) -> list[OpportunityDelta]:
        return [
            delta
            for delta in self.deltas
            if delta.status in {"new", "removed"} or delta.action_changed
        ]


def compare_opportunities(
    previous: list[StoredOpportunityRecord],
    latest: list[StoredOpportunityRecord],
    previous_run_id: int | None = None,
    latest_run_id: int | None = None,
) -> SnapshotComparison:
    previous_by_name = {record.item_name: record for record in previous}
    latest_by_name = {record.item_name: record for record in latest}
    item_names = sorted(set(previous_by_name) | set(latest_by_name))
    deltas: list[OpportunityDelta] = []

    for item_name in item_names:
        previous_record = previous_by_name.get(item_name)
        latest_record = latest_by_name.get(item_name)

        if previous_record is None and latest_record is not None:
            deltas.append(
                OpportunityDelta(
                    item_name=item_name,
                    status="new",
                    latest_score=latest_record.opportunity_score,
                    latest_action=latest_record.action,
                )
            )
            continue

        if latest_record is None and previous_record is not None:
            deltas.append(
                OpportunityDelta(
                    item_name=item_name,
                    status="removed",
                    previous_score=previous_record.opportunity_score,
                    previous_action=previous_record.action,
                )
            )
            continue

        if previous_record is None or latest_record is None:
            continue

        score_delta = round(
            latest_record.opportunity_score - previous_record.opportunity_score,
            2,
        )
        deltas.append(
            OpportunityDelta(
                item_name=item_name,
                status="changed",
                previous_score=previous_record.opportunity_score,
                latest_score=latest_record.opportunity_score,
                score_delta=score_delta,
                previous_action=previous_record.action,
                latest_action=latest_record.action,
                action_changed=previous_record.action != latest_record.action,
            )
        )

    return SnapshotComparison(
        previous_run_id=previous_run_id,
        latest_run_id=latest_run_id,
        deltas=deltas,
    )
