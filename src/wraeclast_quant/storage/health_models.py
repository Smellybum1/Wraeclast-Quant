from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class DatabaseHealthError(ValueError):
    """Raised when a local SQLite database cannot be checked."""


@dataclass(frozen=True)
class DatabaseHealthResult:
    database_path: Path
    schema_version: str
    required_tables: list[str]
    size_bytes: int
    integrity_ok: bool
    integrity_message: str
    missing_tables: list[str]
    analysis_run_count: int | None
    scored_opportunity_count: int | None
    report_artifact_count: int | None
    recommendation_outcome_count: int | None
    latest_run_id: int | None
    latest_run_created_at: str | None
    latest_run_source_mode: str | None
    latest_run_item_count: int | None

    @property
    def schema_ok(self) -> bool:
        return not self.missing_tables

    @property
    def ok(self) -> bool:
        return self.integrity_ok and self.schema_ok
