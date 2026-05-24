from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.site_bundle import (
    DEFAULT_SITE_BUNDLE_DIR,
    SiteBundleError,
    write_site_bundle,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR

console = Console(width=260)


def register(app: typer.Typer) -> None:
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
