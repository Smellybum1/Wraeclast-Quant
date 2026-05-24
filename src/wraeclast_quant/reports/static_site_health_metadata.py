from __future__ import annotations

import re
from typing import Any


def meta_content(html: str, name: str) -> str:
    match = re.search(
        rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)">',
        html,
        re.IGNORECASE,
    )
    return match.group(1) if match else ""


def optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


__all__ = ["meta_content", "optional_int"]
