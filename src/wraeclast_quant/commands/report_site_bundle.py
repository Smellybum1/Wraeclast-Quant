from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.report_site_bundle_rendering import (
    print_site_bundle_error,
    print_site_bundle_result,
)
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.site_bundle import (
    DEFAULT_SITE_BUNDLE_DIR,
    SiteBundleError,
    write_site_bundle,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR


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
            print_site_bundle_error(str(error))
            raise typer.Exit(code=1) from error

        print_site_bundle_result(result)
