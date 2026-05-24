from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


def fetch_plan_for_report(review: ConnectorReview, resources: list[Resource]):
    try:
        from wraeclast_quant.config.fetch_policy import build_fetch_plan

        return build_fetch_plan(review, resources).plan
    except ConnectorPolicyError:
        return None
