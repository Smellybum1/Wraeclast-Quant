from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.report_site_contract_rendering import print_site_contract_result
from wraeclast_quant.reports.site_bundle import DEFAULT_SITE_BUNDLE_DIR
from wraeclast_quant.reports.site_contract import (
    DEFAULT_SITE_CONTRACT_PATH,
    write_site_contract,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH


def register(app: typer.Typer) -> None:
    @app.command("site-contract")
    def site_contract(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        bundle_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--bundle-dir"),
        output_path: Path = typer.Option(DEFAULT_SITE_CONTRACT_PATH, "--output-path"),
        strict: bool = typer.Option(False, "--strict", help="Exit nonzero when site contract readiness fails."),
    ) -> None:
        written_path, payload = write_site_contract(
            database_path=database_path,
            bundle_dir=bundle_dir,
            output_path=output_path,
        )
        readiness = payload["publish_readiness"]

        print_site_contract_result(written_path, payload)
        if strict and not readiness["ready"]:
            raise typer.Exit(code=1)
