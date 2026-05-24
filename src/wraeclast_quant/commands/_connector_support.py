from __future__ import annotations

import hashlib
from pathlib import Path

from rich.console import Console

from wraeclast_quant.config.resources_loader import load_resources

console = Console(width=260)
FIXTURE_RESOURCES_PATH = Path("examples/connector_fixture_resources.md")


def load_fixture_resources(resources_path: Path):
    resources = load_resources(resources_path)
    if FIXTURE_RESOURCES_PATH.exists():
        resources.extend(load_resources(FIXTURE_RESOURCES_PATH))
    return resources


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
