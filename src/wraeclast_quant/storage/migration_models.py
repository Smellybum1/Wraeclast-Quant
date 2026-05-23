from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MigrationReadinessCheck:
    key: str
    check: str
    status: str
    details: str


@dataclass(frozen=True)
class MigrationReadinessResult:
    ready: bool
    schema_version: str
    latest_database_run_id: int | None
    latest_backup_run_id: int | None
    checks: list[MigrationReadinessCheck]
    blockers: list[str]
