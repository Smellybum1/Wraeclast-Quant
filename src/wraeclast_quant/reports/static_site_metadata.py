from __future__ import annotations

from html import escape
from typing import Any


def metadata_tags(payload: dict[str, Any], latest_run: dict[str, Any]) -> list[str]:
    metadata = [
        ("wq:schema-version", payload.get("schema_version", "")),
        ("wq:generated-at", payload.get("generated_at", "")),
        ("wq:latest-run-id", latest_run.get("id", "")),
        ("wq:latest-run-source-mode", latest_run.get("source_mode", "")),
        ("wq:latest-run-item-count", latest_run.get("item_count", "")),
    ]
    return [
        f'  <meta name="{escape(name, quote=True)}" content="{escape(str(value), quote=True)}">'
        for name, value in metadata
    ]


__all__ = ["metadata_tags"]
