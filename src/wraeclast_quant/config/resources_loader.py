from __future__ import annotations

from pathlib import Path

from wraeclast_quant.config.resource_models import Resource
from wraeclast_quant.config.resource_parser import parse_resources_markdown
from wraeclast_quant.config.resource_type_inference import infer_resource_type


def load_resources(path: str | Path = "RESOURCES.md") -> list[Resource]:
    resource_path = Path(path)
    return parse_resources_markdown(resource_path.read_text(encoding="utf-8"))


__all__ = [
    "Resource",
    "infer_resource_type",
    "load_resources",
    "parse_resources_markdown",
]
