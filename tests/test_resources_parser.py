from wraeclast_quant.config.resources_loader import (
    infer_resource_type,
    parse_resources_markdown,
)


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
