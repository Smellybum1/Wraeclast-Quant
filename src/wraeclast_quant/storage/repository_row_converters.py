from __future__ import annotations

import json
import sqlite3

from wraeclast_quant.storage.models import (
    AnalysisRunRecord,
    OutcomeReviewRecord,
    RecommendationOutcomeRecord,
    ReportArtifactRecord,
    RunProvenanceRecord,
    StoredOpportunityRecord,
)


def analysis_run_from_row(row: sqlite3.Row) -> AnalysisRunRecord:
    return AnalysisRunRecord(
        id=int(row["id"]),
        created_at=str(row["created_at"]),
        source_mode=str(row["source_mode"]),
        item_count=int(row["item_count"]),
    )


def stored_opportunity_from_row(row: sqlite3.Row) -> StoredOpportunityRecord:
    inputs = json.loads(str(row["inputs_json"]))
    return StoredOpportunityRecord(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        item_name=str(row["item_name"]),
        opportunity_score=float(row["opportunity_score"]),
        action=str(row["action"]),
        inputs={str(key): float(value) for key, value in inputs.items()},
    )


def report_artifact_from_row(row: sqlite3.Row) -> ReportArtifactRecord:
    return ReportArtifactRecord(
        id=int(row["id"]),
        run_id=int(row["run_id"]),
        path=str(row["path"]),
        created_at=str(row["created_at"]),
    )


def run_provenance_from_row(row: sqlite3.Row) -> RunProvenanceRecord:
    return RunProvenanceRecord(
        run_id=int(row["run_id"]),
        source_kind=str(row["source_kind"]),
        resource_name=str(row["resource_name"]),
        connector_id=str(row["connector_id"]),
        access_method=str(row["access_method"]),
        metadata=json.loads(str(row["metadata_json"])),
        created_at=str(row["created_at"]),
    )


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


__all__ = [
    "analysis_run_from_row",
    "outcome_review_from_row",
    "recommendation_outcome_from_row",
    "report_artifact_from_row",
    "run_provenance_from_row",
    "stored_opportunity_from_row",
]
