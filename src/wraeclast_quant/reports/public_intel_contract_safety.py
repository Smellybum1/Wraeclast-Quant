from __future__ import annotations

import re
from typing import Any

RAW_FIELD_NAMES = {"inputs", "notes", "url", "urls", "resources", "raw_resources"}
URL_RE = re.compile(r"https?://", re.IGNORECASE)


def derived_only_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            child_path = f"{path}.{key}"
            if normalized in RAW_FIELD_NAMES:
                errors.append(f"Raw/private field is not allowed: {child_path}")
            errors.extend(derived_only_errors(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(derived_only_errors(child, f"{path}[{index}]"))
    elif isinstance(value, str) and URL_RE.search(value):
        errors.append(f"Raw URL is not allowed: {path}")
    return errors


__all__ = ["RAW_FIELD_NAMES", "URL_RE", "derived_only_errors"]
