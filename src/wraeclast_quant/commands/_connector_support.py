from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from wraeclast_quant.config.resources_loader import load_resources

console = Console(width=260)
FIXTURE_RESOURCES_PATH = Path("examples/connector_fixture_resources.md")


def load_fixture_resources(resources_path: Path):
    resources = load_resources(resources_path)
    if FIXTURE_RESOURCES_PATH.exists():
        resources.extend(load_resources(FIXTURE_RESOURCES_PATH))
    return resources


def print_connector_review_status(status: Any) -> None:
    table = Table(title="Connector Review Status")
    for column in ["Check", "Value", "Status"]:
        table.add_column(column, no_wrap=column != "Value")

    for row in status.rows:
        table.add_row(row.check, row.value, row.status)

    blockers = status.check_result.blockers
    blockers_text = "\n".join(blockers) if blockers else "None"
    table.add_row("Blockers", blockers_text, "blocked" if blockers else "ok")
    console.print(table)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
