from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.public_intel_contract import (
    PublicIntelContractError,
    validate_public_intel_file,
)
from wraeclast_quant.reports.site_bundle import (
    DEFAULT_SITE_BUNDLE_DIR,
    SiteBundleError,
    write_site_bundle,
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

    @app.command("validate-intel")
    def validate_intel(
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
    ) -> None:
        try:
            result = validate_public_intel_file(intel_path)
        except PublicIntelContractError as error:
            raise typer.BadParameter(str(error)) from error

        table = Table(title="Public Intel Contract Validation")
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Path", str(result.path))
        table.add_row("Valid", "yes" if result.valid else "no")
        table.add_row("Schema version", result.schema_version)
        table.add_row("Latest run", str(result.latest_run_id or "none"))
        table.add_row("Top opportunities", str(result.top_opportunities_count))
        table.add_row("Alerts", str(result.alerts_count))
        table.add_row("Errors", "\n".join(result.errors) if result.errors else "None")
        console.print(table)
        if not result.valid:
            raise typer.Exit(code=1)
        console.print("Public intel export matches the local derived-only contract.")

    @app.command("site-bundle")
    def site_bundle(
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
        output_dir: Path = typer.Option(DEFAULT_SITE_BUNDLE_DIR, "--output-dir"),
    ) -> None:
        try:
            result = write_site_bundle(
                intel_path=intel_path,
                site_dir=site_dir,
                output_dir=output_dir,
            )
        except SiteBundleError as error:
            console.print(str(error))
            raise typer.Exit(code=1) from error

        table = Table(title="Local Site Bundle")
        table.add_column("Artifact")
        table.add_column("Path")
        table.add_row("Bundle directory", str(result.bundle_dir))
        table.add_row("Archive", str(result.archive_path))
        table.add_row("Files", ", ".join(result.files))
        table.add_row("Generated", result.generated_at)
        console.print(table)
        console.print("Bundle is local-only. No publishing, hosting, or network requests were performed.")
