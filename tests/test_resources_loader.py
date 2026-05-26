from pathlib import Path

from wraeclast_quant.config.preflight import assess_preflight_resource
from wraeclast_quant.config.resources_loader import infer_resource_type, load_resources, parse_resources_markdown

from cli_doc_markdown_helpers import documented_bullets as _documented_bullets
from cli_doc_markdown_helpers import documented_mapping as _documented_mapping


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


def test_resource_defaults_and_inference() -> None:
    markdown = """
## Price Data
- [Example Market](https://example.test/economy/items)

## Other
- name: Mystery Source
  url: https://example.test/feed
"""
    resources = parse_resources_markdown(markdown)

    assert resources[0].type == "price_site"
    assert resources[0].priority == "medium"
    assert resources[0].allowed_use == "manual-review"
    assert resources[1].type == "unknown"


def test_parser_tolerates_utf8_bom_before_first_heading() -> None:
    markdown = "\ufeff## Official Sources\n- name: Approved API\n  url: https://example.test/api\n  allowed_use: api\n"

    resources = parse_resources_markdown(markdown)

    assert len(resources) == 1
    assert resources[0].name == "Approved API"
    assert resources[0].allowed_use == "api"


def test_simple_table() -> None:
    markdown = """
## Build Data
| name | url | priority |
| --- | --- | --- |
| Example Builds | https://example.test/builds | high |
"""
    resources = parse_resources_markdown(markdown)

    assert resources[0].name == "Example Builds"
    assert resources[0].type == "build_site"


def test_infer_resource_type_from_url() -> None:
    assert infer_resource_type(url="https://www.reddit.com/r/PathOfExile2/") == "social"


def test_resource_configuration_contract_doc_matches_loader_defaults() -> None:
    doc_text = Path("docs/RESOURCE_CONFIGURATION.md").read_text(encoding="utf-8")
    documented_defaults = _documented_mapping(doc_text, "If metadata is missing, the loader uses these safe defaults:")
    documented_types = _documented_bullets(doc_text, "Current type inference recognizes:")
    resource = parse_resources_markdown(
        """
## Other
- Mystery Source
"""
    )[0]

    assert documented_defaults == {
        "type": "unknown",
        "priority": "medium",
        "allowed_use": "manual-review",
        "reliability": "unknown",
        "id": "",
        "url": "",
        "collector": "",
        "refresh": "",
        "notes": "",
    }
    assert {
        key: str(getattr(resource, key))
        for key in documented_defaults
    } == documented_defaults
    assert documented_types == {
        "price_site",
        "build_site",
        "social",
        "youtube",
        "official",
        "unknown",
    }
