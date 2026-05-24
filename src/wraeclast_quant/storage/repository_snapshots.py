from __future__ import annotations

from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.storage.models import AnalysisRunRecord, StoredOpportunityRecord
from wraeclast_quant.storage.repository_snapshot_queries import (
    analysis_run_query,
    latest_run_query,
    list_recent_runs_query,
    previous_run_before_query,
    scored_opportunities_for_run_query,
)
from wraeclast_quant.storage.repository_snapshot_writes import (
    create_analysis_run_record,
    save_scored_opportunity_records,
)


class SnapshotDataMixin:
    def create_analysis_run(
        self,
        source_mode: str,
        item_count: int,
        created_at: str | None = None,
    ) -> AnalysisRunRecord:
        return create_analysis_run_record(
            self.database_path,
            source_mode=source_mode,
            item_count=item_count,
            created_at=created_at,
        )

    def save_scored_opportunities(
        self,
        run_id: int,
        opportunities: list[ScoredOpportunity],
    ) -> None:
        save_scored_opportunity_records(self.database_path, run_id, opportunities)

    def latest_run(self) -> AnalysisRunRecord | None:
        return latest_run_query(self.database_path)

    def previous_run_before(self, run_id: int) -> AnalysisRunRecord | None:
        return previous_run_before_query(self.database_path, run_id)

    def analysis_run(self, run_id: int) -> AnalysisRunRecord | None:
        return analysis_run_query(self.database_path, run_id)

    def list_recent_runs(self, limit: int = 5) -> list[AnalysisRunRecord]:
        return list_recent_runs_query(self.database_path, limit=limit)

    def latest_scored_opportunities(self, limit: int = 5) -> list[StoredOpportunityRecord]:
        latest = self.latest_run()
        if latest is None:
            return []
        return self.scored_opportunities_for_run(latest.id, limit=limit)

    def scored_opportunities_for_run(
        self,
        run_id: int,
        limit: int | None = None,
    ) -> list[StoredOpportunityRecord]:
        return scored_opportunities_for_run_query(self.database_path, run_id, limit=limit)
