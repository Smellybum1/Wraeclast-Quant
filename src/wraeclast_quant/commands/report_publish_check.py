from __future__ import annotations

import json
from pathlib import Path

import typer

from wraeclast_quant.commands.report_publish_check_rendering import print_publish_check_result
from wraeclast_quant.reports.publish_check import (
    check_publish_readiness,
    publish_check_payload,
)
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command("publish-check")
    def publish_check(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when publishing readiness fails."),
        json_output: bool = typer.Option(False, "--json", help="Print publish readiness as JSON."),
    ) -> None:
        result = check_publish_readiness(database_path=database_path, bundle_dir=bundle_dir)
        if json_output:
            typer.echo(json.dumps(publish_check_payload(result), indent=2, sort_keys=True))
        else:
            print_publish_check_result(result)
        if strict and not result.ready:
            raise typer.Exit(code=1)
