from pathlib import Path

from wraeclast_quant.config.resources_loader import parse_resources_markdown

from cli_doc_markdown_helpers import documented_bullets as _documented_bullets
from cli_doc_markdown_helpers import documented_mapping as _documented_mapping


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
