from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.preflight import PreflightAssessment
from wraeclast_quant.config.resources_loader import Resource


class ConnectorCandidate(BaseModel):
    resource: Resource
    preflight: PreflightAssessment
    suggested_access_method: str
    draft_command: str
    recommendation: str
    rank: int
