from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.report_validate_intel_rendering import (
    print_public_intel_validation,
    print_public_intel_validation_success,
)
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)


def register(app: typer.Typer) -> None:
    @app.command("validate-intel")
    def validate_intel(
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
    ) -> None:
        try:
            result = validate_public_intel_file(intel_path)
        except PublicIntelContractError as error:
            raise typer.BadParameter(str(error)) from error

        print_public_intel_validation(result)
        if not result.valid:
            raise typer.Exit(code=1)
        print_public_intel_validation_success()
