from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.config.connector_policy import ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


def eligible_resource(*, resource_id: str | None = None) -> Resource:
    data = dict(
        name="Approved API",
        type="official",
        url="https://example.test/api",
        allowed_use="api",
    )
    if resource_id is not None:
        data["id"] = resource_id
    return Resource(**data)


def eligible_rss_resource(*, resource_id: str | None = None) -> Resource:
    data = dict(
        name="Approved API",
        type="official",
        url="https://example.test/feed.xml",
        allowed_use="rss",
    )
    if resource_id is not None:
        data["id"] = resource_id
    return Resource(**data)


def eligible_download_resource(*, resource_id: str | None = None) -> Resource:
    data = dict(
        name="Approved Download",
        type="official",
        url="https://example.test/data.json",
        allowed_use="download",
    )
    if resource_id is not None:
        data["id"] = resource_id
    return Resource(**data)


def poe_ninja_currency_resource() -> Resource:
    return Resource(
        id="poe_ninja_poe2_currency",
        name="poe.ninja POE2 Currency",
        type="price_site",
        url="https://poe.ninja/poe2/economy/vaal/currency",
        allowed_use="api",
    )


def poe_ninja_currency_review_resource() -> Resource:
    return Resource(
        id="poe_ninja_poe2_currency",
        name="poe.ninja POE2 Currency",
        type="price_site",
        url="https://poe.ninja/poe2/economy/vaal/currency",
        allowed_use="manual-or-api-if-available",
    )


def conditional_api_resource(
    *,
    resource_id: str | None = "conditional_api",
    resource_type: str | None = "price_site",
    url: str = "https://example.test/api",
    allowed_use: str = "manual-or-api-if-available",
    priority: str | None = None,
    notes: str | None = None,
) -> Resource:
    data = dict(
        name="Conditional API",
        url=url,
        allowed_use=allowed_use,
    )
    if resource_id is not None:
        data["id"] = resource_id
    if resource_type is not None:
        data["type"] = resource_type
    if priority is not None:
        data["priority"] = priority
    if notes is not None:
        data["notes"] = notes
    return Resource(**data)


def discord_resource(
    *,
    name: str = "Official Discord",
    url: str = "https://discord.gg/example",
    allowed_use: str = "api",
) -> Resource:
    return Resource(
        name=name,
        type="discord",
        url=url,
        allowed_use=allowed_use,
    )


def example_approved_api_resources() -> list[Resource]:
    return [
        Resource(
            name="Example Approved API",
            type="official",
            url="https://example.test/api",
            allowed_use="api",
        )
    ]


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


def write_connector_fixture(tmp_path: Path, payload: dict[str, object]) -> Path:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(payload), encoding="utf-8")
    return fixture_path


def missing_items_fixture_payload() -> dict[str, object]:
    return {"source_name": "Example Approved API", "generated_at": "now"}


def unnamed_item_fixture_payload() -> dict[str, object]:
    return {
        "source_name": "Example Approved API",
        "generated_at": "now",
        "items": [{"category": "currency"}],
    }


def invalid_signals_fixture_payload() -> dict[str, object]:
    return {
        "source_name": "Example Approved API",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "items": [
            {
                "name": "Stormglass Catalyst",
                "signals": {
                    "demand_momentum": 101,
                    "build_dependency_score": 82,
                    "price_discount_score": 76,
                    "liquidity_score": 70,
                    "historical_spike_score": 68,
                    "patch_relevance_score": 74,
                    "manipulation_risk": 18,
                    "stale_data_penalty": 8,
                },
            }
        ],
    }


def minimal_fixture_payload() -> dict[str, object]:
    return {
        "source_name": "Approved API",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "items": [{"name": "Stormglass Catalyst"}],
    }


__all__ = [
    "conditional_api_resource",
    "connector_review",
    "connector_review_payload",
    "discord_resource",
    "eligible_download_resource",
    "eligible_resource",
    "eligible_rss_resource",
    "example_approved_api_resources",
    "invalid_signals_fixture_payload",
    "minimal_fixture_payload",
    "missing_items_fixture_payload",
    "unnamed_item_fixture_payload",
    "poe_ninja_currency_resource",
    "poe_ninja_currency_review_resource",
    "write_connector_fixture",
]
