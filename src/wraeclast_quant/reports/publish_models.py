from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PublishCheckRow:
    key: str
    check: str
    status: str
    details: str


@dataclass(frozen=True)
class PublishCheckResult:
    ready: bool
    latest_database_run_id: int | None
    bundle_latest_run_id: int | None
    archive_path: Path
    files: list[str]
    checks: list[PublishCheckRow]
    blockers: list[str]
