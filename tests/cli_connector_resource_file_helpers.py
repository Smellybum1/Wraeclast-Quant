from __future__ import annotations

from pathlib import Path


def write_connector_resources(tmp_path: Path, text: str) -> Path:
    resources_path = tmp_path / "RESOURCES.md"
    resources_path.write_text(text, encoding="utf-8")
    return resources_path


__all__ = ["write_connector_resources"]
