from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ALLOWED_ACCESS_METHODS,
    ConnectorPolicyError,
    ConnectorReview,
)
from wraeclast_quant.config.connector_policy_utils import find_resource
from wraeclast_quant.config.resources_loader import Resource


def build_connector_review_draft(
    resource_name: str,
    access_method: str,
    resources: list[Resource],
) -> ConnectorReview:
    resource = find_resource(resource_name, resources)
    if resource is None:
        raise ConnectorPolicyError("No matching resource found in RESOURCES.md.")
    if resource.type.strip().lower() == "discord":
        raise ConnectorPolicyError(
            "Discord resources require explicit approved-bot/API review before drafting."
        )
    if access_method not in ALLOWED_ACCESS_METHODS:
        raise ConnectorPolicyError(
            "access_method must be one of api, rss, download, or manual-export."
        )

    return ConnectorReview(
        resource_name=resource.name,
        access_method=access_method,
        source_terms_reviewed=False,
        robots_or_api_policy_reviewed=False,
        source_terms_url="",
        robots_or_api_policy_url="",
        reviewed_at="",
        review_notes="",
        allowed_data_shape="",
        authentication_required=False,
        login_required=False,
        captcha_gated=False,
        private_data_risk=False,
        rate_limit_per_minute=6,
        cache_ttl_seconds=86400,
        dry_run_supported=True,
        public_export_derived_only=True,
    )
