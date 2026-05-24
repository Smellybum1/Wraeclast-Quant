from __future__ import annotations

from wraeclast_quant.config.connector_candidate_builder import candidate_from_assessment
from wraeclast_quant.config.connector_candidate_models import ConnectorCandidate
from wraeclast_quant.config.connector_candidate_priority import priority_rank
from wraeclast_quant.config.preflight import assess_preflight_resources
from wraeclast_quant.config.resources_loader import Resource


def connector_candidates(resources: list[Resource], limit: int = 10) -> list[ConnectorCandidate]:
    candidates = [candidate_from_assessment(assessment) for assessment in assess_preflight_resources(resources)]
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            candidate.rank,
            priority_rank(candidate.resource.priority),
            candidate.resource.name.casefold(),
        ),
    )
    return ranked[:limit]
