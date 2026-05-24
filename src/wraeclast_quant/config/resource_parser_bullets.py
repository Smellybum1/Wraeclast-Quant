from __future__ import annotations

import re

from wraeclast_quant.config.resource_parser_text import KEY_VALUE_RE, normalize_key

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
URL_RE = re.compile(r"https?://\S+")


def parse_bullet(text: str) -> dict[str, str]:
    if text.lstrip().startswith("#"):
        return {}

    key_value = KEY_VALUE_RE.match(text)
    if key_value:
        return {normalize_key(key_value.group(1)): key_value.group(2).strip()}

    link = LINK_RE.search(text)
    if link:
        return {"name": link.group(1).strip(), "url": link.group(2).strip()}

    url = URL_RE.search(text)
    if url:
        name = text.replace(url.group(0), "").strip(" -:")
        return {"name": name or url.group(0), "url": url.group(0)}

    return {"name": text.strip()}
