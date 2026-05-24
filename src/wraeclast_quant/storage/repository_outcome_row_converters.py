from __future__ import annotations

import sqlite3

from wraeclast_quant.storage.models import OutcomeReviewRecord, RecommendationOutcomeRecord


def recommendation_outcome_from_row(row: sqlite3.Row) -> RecommendationOutcomeRecord:
    return RecommendationOutcomeRecord(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        item_name=str(row["item_name"]),
        outcome=str(row["outcome"]),
        notes=str(row["notes"]),
        observed_at=str(row["observed_at"]),
    )


def outcome_review_from_row(row: sqlite3.Row) -> OutcomeReviewRecord:
    return OutcomeReviewRecord(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        item_name=str(row["item_name"]),
        outcome=str(row["outcome"]),
        notes=str(row["notes"]),
        observed_at=str(row["observed_at"]),
        opportunity_score=float(row["opportunity_score"]),
        action=str(row["action"]),
    )


__all__ = ["outcome_review_from_row", "recommendation_outcome_from_row"]
