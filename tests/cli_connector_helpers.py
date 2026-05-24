from __future__ import annotations

import json
from pathlib import Path


def connector_review(**overrides) -> dict[str, object]:
    review = {
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
    review.update(overrides)
    return review


def approved_api_resources_text(*, include_id: bool = True) -> str:
    id_line = "- id: approved_api\n  " if include_id else "- "
    return f"""
## Official Sources
{id_line}name: Approved API
  type: official
  url: https://example.test/api
  allowed_use: api
"""


def conditional_api_resources_text(*, include_id: bool = True) -> str:
    id_line = "- id: conditional_api\n  " if include_id else "- "
    return f"""
## Price Data
{id_line}name: Conditional API
  type: price_site
  url: https://example.test/api
  allowed_use: manual-or-api-if-available
"""


def discord_resources_text() -> str:
    return """
## Discord Signals
- name: Official Discord
  type: discord
  url: https://discord.gg/example
  allowed_use: api
"""


def manual_source_resources_text() -> str:
    return """
## Official Sources
- name: Manual Source
  type: official
  url: https://example.test
  allowed_use: manual-review
"""


def poe_ninja_currency_resources_text(
    *,
    allowed_use: str = "api",
    include_manual_source: bool = False,
) -> str:
    manual_source = (
        "- name: Manual Source\n"
        "  type: manual_workflow\n"
        "  priority: critical\n"
        "  allowed_use: manual-review\n"
        if include_manual_source
        else ""
    )
    return f"""
## Price Data
- id: poe_ninja_poe2_currency
  name: poe.ninja POE2 Currency
  type: price_site
  url: https://poe.ninja/poe2/economy/vaal/currency
  priority: high
  allowed_use: {allowed_use}
{manual_source}"""


def write_connector_resources(tmp_path: Path, text: str) -> Path:
    resources_path = tmp_path / "RESOURCES.md"
    resources_path.write_text(text, encoding="utf-8")
    return resources_path


def write_connector_review(tmp_path: Path, **overrides) -> Path:
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(connector_review(**overrides)), encoding="utf-8")
    return review_path


__all__ = [
    "approved_api_resources_text",
    "conditional_api_resources_text",
    "connector_review",
    "discord_resources_text",
    "manual_source_resources_text",
    "poe_ninja_currency_resources_text",
    "write_connector_resources",
    "write_connector_review",
]
