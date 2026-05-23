from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_BACKUP_DIR = Path("data/backups")


class DatabaseBackupError(ValueError):
    """Raised when a local SQLite backup cannot be created."""


@dataclass(frozen=True)
class DatabaseBackupResult:
    source_path: Path
    backup_path: Path
    created_at: str
    size_bytes: int


@dataclass(frozen=True)
class DatabaseBackupVerification:
    backup_path: Path
    schema_version: str
    required_tables: list[str]
    size_bytes: int
    analysis_run_count: int
    scored_opportunity_count: int
    report_artifact_count: int
    recommendation_outcome_count: int
    latest_run_id: int | None
    latest_run_created_at: str | None
    latest_run_source_mode: str | None
    latest_run_item_count: int | None


@dataclass(frozen=True)
class DatabaseBackupListing:
    backup_path: Path
    modified_at: str
    size_bytes: int
    valid: bool
    analysis_run_count: int | None
    latest_run_id: int | None
    latest_run_source_mode: str | None
    error: str


@dataclass(frozen=True)
class DatabaseRestoreGuidance:
    backup_path: Path
    database_path: Path
    backup_size_bytes: int
    latest_run_id: int | None
    latest_run_source_mode: str | None
    latest_run_item_count: int | None
    target_exists: bool
    target_parent_exists: bool
    powershell_command: str
