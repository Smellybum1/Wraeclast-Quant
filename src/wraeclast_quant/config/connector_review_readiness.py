from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import (
    ALLOWED_ACCESS_METHODS,
    ConnectorCheckResult,
    ConnectorReview,
)
from wraeclast_quant.config.connector_policy_utils import find_resource
from wraeclast_quant.config.preflight import assess_preflight_resource
from wraeclast_quant.config.resources_loader import Resource


def check_connector_review(
    review: ConnectorReview,
    resources: list[Resource],
) -> ConnectorCheckResult:
    resource = find_resource(review.resource_name, resources)
    blockers: list[str] = []
    preflight = None

    if resource is None:
        blockers.append("No matching resource found in RESOURCES.md.")
    else:
        preflight = assess_preflight_resource(resource)
        if not preflight.automation_eligible:
            blockers.append(
                f"Resource is not automation-eligible: {preflight.status} - {preflight.reason}"
            )
        if resource.type.strip().lower() == "discord":
            blockers.append("Discord resources require explicit approved-bot/API review.")

    if review.access_method not in ALLOWED_ACCESS_METHODS:
        blockers.append(
            "access_method must be one of api, rss, download, or manual-export."
        )
    if not review.source_terms_reviewed:
        blockers.append("Source terms must be reviewed.")
    elif not review.source_terms_url.strip():
        blockers.append("source_terms_url is required when source terms are reviewed.")
    if not review.robots_or_api_policy_reviewed:
        blockers.append("Robots.txt or API policy must be reviewed.")
    elif not review.robots_or_api_policy_url.strip():
        blockers.append(
            "robots_or_api_policy_url is required when robots/API policy is reviewed."
        )
    if review.source_terms_reviewed and review.robots_or_api_policy_reviewed:
        if not review.reviewed_at.strip():
            blockers.append("reviewed_at is required when review confirmations are complete.")
        if not review.allowed_data_shape.strip():
            blockers.append(
                "allowed_data_shape is required when review confirmations are complete."
            )
    if review.authentication_required:
        blockers.append("Authentication-required sources are not eligible in this gate.")
    if review.login_required:
        blockers.append("Login-required sources are not eligible in this gate.")
    if review.captcha_gated:
        blockers.append("CAPTCHA-gated sources are not eligible.")
    if review.private_data_risk:
        blockers.append("Private data or private-message risk is not eligible.")
    if review.rate_limit_per_minute <= 0:
        blockers.append("rate_limit_per_minute must be positive.")
    if review.cache_ttl_seconds <= 0:
        blockers.append("cache_ttl_seconds must be positive.")
    if not review.dry_run_supported:
        blockers.append("Dry-run support must be explicitly confirmed.")
    if not review.public_export_derived_only:
        blockers.append("Public export must be derived-only.")

    return ConnectorCheckResult(
        review=review,
        resource=resource,
        preflight=preflight,
        ready=not blockers,
        blockers=blockers,
    )
