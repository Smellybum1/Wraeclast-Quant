from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.resources_loader import Resource


class PreflightAssessment(BaseModel):
    resource: Resource
    collector: str
    status: str
    automation_eligible: bool
    reason: str
    next_step: str
    placeholder_only: bool = True


class PreflightSummary(BaseModel):
    total: int
    eligible: int
    manual_review: int
    needs_review: int
    blocked: int
    discord_gated: int
    placeholder_only: int
