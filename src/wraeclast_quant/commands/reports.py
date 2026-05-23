from __future__ import annotations

import typer

from wraeclast_quant.commands import report_artifacts, report_exports, report_publishing


def register(app: typer.Typer) -> None:
    report_exports.register(app)
    report_artifacts.register(app)
    report_publishing.register(app)
