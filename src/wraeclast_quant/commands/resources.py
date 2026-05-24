from __future__ import annotations

import typer

from wraeclast_quant.commands import resource_collect, resource_compliance, resource_preflight


def register(app: typer.Typer) -> None:
    resource_collect.register(app)
    resource_compliance.register(app)
    resource_preflight.register(app)
