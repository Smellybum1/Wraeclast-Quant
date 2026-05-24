from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class PublicIntelContractError(ValueError):
    """Raised when a local public-intel export cannot be loaded."""


@dataclass(frozen=True)
class PublicIntelValidationResult:
    path: Path
    valid: bool
    schema_version: str
    latest_run_id: int | None
    top_opportunities_count: int
    alerts_count: int
    errors: list[str]
