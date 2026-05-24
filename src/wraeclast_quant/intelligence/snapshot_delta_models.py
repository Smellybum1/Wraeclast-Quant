from __future__ import annotations

from pydantic import BaseModel


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


__all__ = ["OpportunityDelta", "SnapshotComparison"]
