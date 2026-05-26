from pathlib import Path

from wraeclast_quant.config.preflight import assess_preflight_resource
from wraeclast_quant.config.resources_loader import load_resources


def test_parses_existing_resources_file() -> None:
    resources = load_resources(Path("RESOURCES.md"))

    names = {resource.name for resource in resources}
    types = {resource.type for resource in resources}

    assert "POE2 Scout Currency" in names
    assert "Official Path of Exile 2 Discord" in names
    assert "Path of Exile 2 Official Trade" in names
    assert "Respect each site's terms, robots.txt, and API limits." not in names
    assert "price_site" in types
    assert "build_site" in types
    assert "discord" in types
    assert any(resource.id == "poe2_scout_currency" for resource in resources)
    assert any(resource.collector == "discord_placeholder" for resource in resources)


def test_official_currency_exchange_resource_is_source_approved_but_auth_gated() -> None:
    resources = load_resources(Path("RESOURCES.md"))
    resource = next(
        resource for resource in resources if resource.id == "official_currency_exchange_api"
    )
    assessment = assess_preflight_resource(resource)

    assert resource.name == "Path of Exile Currency Exchange API"
    assert resource.allowed_use == "api"
    assert "service:cxapi" in resource.notes
    assert "credential storage outside the repo" in resource.notes
    assert assessment.automation_eligible is True
    assert assessment.status == "approved-api"
