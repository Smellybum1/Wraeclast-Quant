from __future__ import annotations

from wraeclast_quant.config.connector_policy import ConnectorReview


def connector_review(**overrides: object) -> ConnectorReview:
    data = connector_review_payload()
    data.update(overrides)
    return ConnectorReview.model_validate(data)


def connector_review_payload() -> dict[str, object]:
    return {
        "resource_name": "Approved API",
        "access_method": "api",
        "source_terms_reviewed": True,
        "robots_or_api_policy_reviewed": True,
        "source_terms_url": "https://example.test/terms",
        "robots_or_api_policy_url": "https://example.test/api-policy",
        "reviewed_at": "2026-05-23",
        "review_notes": "Example local connector review.",
        "allowed_data_shape": "Derived price summary rows only.",
        "authentication_required": False,
        "login_required": False,
        "captcha_gated": False,
        "private_data_risk": False,
        "rate_limit_per_minute": 30,
        "cache_ttl_seconds": 3600,
        "dry_run_supported": True,
        "public_export_derived_only": True,
    }


__all__ = [
    "connector_review",
    "connector_review_payload",
]
