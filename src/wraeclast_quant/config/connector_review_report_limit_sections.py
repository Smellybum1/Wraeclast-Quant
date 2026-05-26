from __future__ import annotations

from wraeclast_quant.config.connector_policy_models import ConnectorReview
from wraeclast_quant.config.connector_policy_utils import yes_no


def safety_section(review: ConnectorReview) -> list[str]:
    return [
        "## Safety Flags",
        "",
        f"- Authentication required: `{yes_no(review.authentication_required)}`",
        f"- Authentication approved: `{yes_no(review.authentication_approved)}`",
        f"- Credential storage reviewed: `{yes_no(review.credential_storage_reviewed)}`",
        f"- Login required: `{yes_no(review.login_required)}`",
        f"- CAPTCHA gated: `{yes_no(review.captcha_gated)}`",
        f"- Private data risk: `{yes_no(review.private_data_risk)}`",
        f"- Dry-run supported: `{yes_no(review.dry_run_supported)}`",
        f"- Derived-only public export: `{yes_no(review.public_export_derived_only)}`",
        "",
    ]


def limits_section(review: ConnectorReview) -> list[str]:
    return [
        "## Limits",
        "",
        f"- Rate limit: `{review.rate_limit_per_minute:g}/min`",
        f"- Cache TTL: `{review.cache_ttl_seconds}s`",
        "",
    ]


__all__ = ["limits_section", "safety_section"]
