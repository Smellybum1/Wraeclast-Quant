from __future__ import annotations


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


__all__ = [
    "approved_api_resources_text",
    "conditional_api_resources_text",
    "discord_resources_text",
    "manual_source_resources_text",
    "poe_ninja_currency_resources_text",
]
