from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.report_site_rendering import (
    print_missing_public_intel_export,
    print_public_intel_contract_errors,
    print_static_site_written,
)
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR, load_public_intel, write_static_site


def register(app: typer.Typer) -> None:
    @app.command()
    def site(
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        output_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--output-dir"),
    ) -> None:
        if not intel_path.exists():
            print_missing_public_intel_export()
            return
        try:
            validation = validate_public_intel_file(intel_path)
        except PublicIntelContractError as error:
            raise typer.BadParameter(str(error)) from error
        if not validation.valid:
            print_public_intel_contract_errors(validation.errors)
            raise typer.Exit(code=1)

        payload = load_public_intel(intel_path)
        if payload is None:
            print_missing_public_intel_export()
            return
        output_path = write_static_site(payload, output_dir)
        print_static_site_written(output_path)
