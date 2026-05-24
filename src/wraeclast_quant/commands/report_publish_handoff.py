from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.report_publish_handoff_rendering import print_publish_handoff_result
from wraeclast_quant.reports.publish_check import (
    DEFAULT_PUBLISH_HANDOFF_PATH,
    check_publish_readiness,
    write_publish_handoff,
)
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command("publish-handoff")
    def publish_handoff(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        output_path: Path = typer.Option(DEFAULT_PUBLISH_HANDOFF_PATH, "--output-path"),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when publishing readiness fails."),
    ) -> None:
        result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)
        written_path = write_publish_handoff(result, output_path)

        print_publish_handoff_result(result, written_path)
        if strict and not result.ready:
            raise typer.Exit(code=1)
