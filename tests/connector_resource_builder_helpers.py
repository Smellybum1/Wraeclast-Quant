from __future__ import annotations

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


__all__ = [
    "conditional_api_resource",
    "discord_resource",
    "eligible_download_resource",
    "eligible_resource",
    "eligible_rss_resource",
    "example_approved_api_resources",
    "poe_ninja_currency_resource",
    "poe_ninja_currency_review_resource",
]
