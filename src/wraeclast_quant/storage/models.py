from pydantic import BaseModel


class AnalysisRunRecord(BaseModel):
    id: int
    created_at: str
    source_mode: str
    item_count: int


class StoredOpportunityRecord(BaseModel):
    id: int
    run_id: int
    item_name: str
    opportunity_score: float
    action: str
    inputs: dict[str, float]


class ReportArtifactRecord(BaseModel):
    id: int
    run_id: int
    path: str
    created_at: str


class RunProvenanceRecord(BaseModel):
    run_id: int
    source_kind: str
    resource_name: str
    connector_id: str
    access_method: str
    metadata: dict[str, object]
    created_at: str


class RecommendationOutcomeRecord(BaseModel):
    id: int
    run_id: int
    item_name: str
    outcome: str
    notes: str
    observed_at: str


class OutcomeReviewRecord(BaseModel):
    id: int
    run_id: int
    item_name: str
    outcome: str
    notes: str
    observed_at: str
    opportunity_score: float
    action: str


class ReviewCoverageRecord(BaseModel):
    run_id: int
    total_recommendations: int
    reviewed_recommendations: int
    unreviewed_recommendations: int
    reviewed_percent: float
