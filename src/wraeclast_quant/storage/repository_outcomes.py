from __future__ import annotations

from wraeclast_quant.storage.models import (
    OutcomeReviewRecord,
    RecommendationOutcomeRecord,
    ReviewCoverageRecord,
    StoredOpportunityRecord,
)
from wraeclast_quant.storage.repository_outcome_coverage import (
    item_exists_for_run_query,
    review_coverage_for_run_query,
)
from wraeclast_quant.storage.repository_outcome_policy import (
    ALLOWED_OUTCOMES,
    normalize_outcome,
)
from wraeclast_quant.storage.repository_outcome_records import (
    list_recent_outcome_records,
    outcome_count_summary,
    recommendation_outcome_exists_query,
    save_recommendation_outcome_record,
    save_recommendation_outcome_records,
)
from wraeclast_quant.storage.repository_outcome_reviews import (
    list_outcome_review_records,
    outcome_review_summary_by_action_query,
    unreviewed_opportunities_for_run_query,
)


class OutcomeReviewMixin:
    def unreviewed_opportunities_for_run(
        self,
        run_id: int,
        limit: int | None = None,
    ) -> list[StoredOpportunityRecord]:
        return unreviewed_opportunities_for_run_query(
            self.database_path,
            run_id,
            limit=limit,
        )

    def save_recommendation_outcome(
        self,
        run_id: int,
        item_name: str,
        outcome: str,
        notes: str = "",
        observed_at: str | None = None,
    ) -> RecommendationOutcomeRecord:
        normalized_outcome = normalize_outcome(outcome)
        if self.analysis_run(run_id) is None:
            raise ValueError(f"analysis run #{run_id} was not found")
        if not self._item_exists_for_run(run_id, item_name):
            raise ValueError(f"item '{item_name}' was not found in analysis run #{run_id}")
        if self.recommendation_outcome_exists(run_id, item_name):
            raise ValueError(
                f"item '{item_name}' already has a recorded outcome for analysis run #{run_id}"
            )

        return save_recommendation_outcome_record(
            self.database_path,
            run_id,
            item_name,
            normalized_outcome,
            notes,
            observed_at,
        )

    def save_recommendation_outcome_batch(
        self,
        run_id: int,
        decisions: list[dict[str, str]],
    ) -> list[RecommendationOutcomeRecord]:
        return save_recommendation_outcome_records(
            self.database_path,
            run_id,
            decisions,
        )

    def list_recent_outcomes(self, limit: int = 20) -> list[RecommendationOutcomeRecord]:
        return list_recent_outcome_records(self.database_path, limit=limit)

    def outcome_summary(self) -> dict[str, int]:
        return outcome_count_summary(self.database_path)

    def list_outcome_reviews(self, limit: int | None = 20) -> list[OutcomeReviewRecord]:
        return list_outcome_review_records(self.database_path, limit=limit)

    def outcome_review_summary_by_action(self) -> dict[str, dict[str, int]]:
        return outcome_review_summary_by_action_query(self.database_path)

    def review_coverage_for_run(self, run_id: int) -> ReviewCoverageRecord:
        return review_coverage_for_run_query(self.database_path, run_id)

    def recommendation_outcome_exists(self, run_id: int, item_name: str) -> bool:
        return recommendation_outcome_exists_query(self.database_path, run_id, item_name)

    def _item_exists_for_run(self, run_id: int, item_name: str) -> bool:
        return item_exists_for_run_query(self.database_path, run_id, item_name)
