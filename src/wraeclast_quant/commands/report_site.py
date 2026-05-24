from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR, load_public_intel, write_static_site

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command()
    def site(
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        output_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--output-dir"),
    ) -> None:
        if not intel_path.exists():
            console.print("No public intel export found. Run wq export first.")
            return
        try:
            validation = validate_public_intel_file(intel_path)
        except PublicIntelContractError as error:
            raise typer.BadParameter(str(error)) from error
        if not validation.valid:
            console.print("Public intel contract validation failed:")
            for error in validation.errors:
                console.print(f"- {error}")
            raise typer.Exit(code=1)

        payload = load_public_intel(intel_path)
        if payload is None:
            console.print("No public intel export found. Run wq export first.")
            return
        output_path = write_static_site(payload, output_dir)
        console.print(f"Wrote local dashboard preview to {output_path}")
