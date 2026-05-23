from __future__ import annotations

SQLITE_SCHEMA_VERSION = "2"

REQUIRED_SQLITE_TABLES = frozenset(
    {
        "analysis_runs",
        "scored_opportunities",
        "report_artifacts",
        "recommendation_outcomes",
        "run_provenance",
    }
)

SQLITE_TABLE_DESCRIPTIONS = {
    "analysis_runs": "One row per scoring/import/report pipeline run.",
    "scored_opportunities": "Ranked item recommendations and deterministic signal inputs.",
    "report_artifacts": "Local report files generated from analysis runs.",
    "recommendation_outcomes": "Manual review outcomes for prior recommendations.",
    "run_provenance": "Local audit metadata for analysis run inputs and connector fixtures.",
}
