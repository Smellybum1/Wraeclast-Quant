from __future__ import annotations

import re

from wraeclast_quant.config.resources_loader import Resource


def suggested_access_method(resource: Resource) -> str:
    allowed_use = resource.allowed_use.strip().lower()
    if "rss" in allowed_use:
        return "rss"
    if "api" in allowed_use:
        return "api"
    if "download" in allowed_use:
        return "download"
    return "manual-export"


def draft_command(resource_ref: str, access_method: str) -> str:
    output_name = _safe_slug(resource_ref) + "_connector_review.json"
    parts = [
        "wq",
        "connector-draft",
        "--resource",
        resource_ref,
        "--access-method",
        access_method,
        "--output-path",
        f"examples/{output_name}",
    ]
    return " ".join(_quote_cli_arg(part) for part in parts)


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return slug.strip("_") or "resource"


def _quote_cli_arg(value: str) -> str:
    if not value or any(character.isspace() for character in value) or '"' in value:
        return f'"{value.replace(chr(34), chr(92) + chr(34))}"'
    return value
