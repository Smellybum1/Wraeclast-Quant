from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.resources_loader import Resource


class ComplianceAssessment(BaseModel):
    resource: Resource
    status: str
    automation_eligible: bool
    reason: str


__all__ = ["ComplianceAssessment"]
