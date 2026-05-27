from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.commands.daily_run_inputs import (
    daily_alert_settings,
    daily_opportunities,
)
from wraeclast_quant.commands.daily_run_rendering import print_daily_result
from wraeclast_quant.reports.public_intel import DEFAULT_PUBLIC_INTEL_PATH
from wraeclast_quant.reports.stash_ninja_watchlist import (
    DEFAULT_STASH_NINJA_WATCHLIST_PATH,
    build_stash_ninja_watchlist,
    write_stash_ninja_watchlist,
    write_stash_ninja_watchlist_markdown,
)
from wraeclast_quant.reports.static_site import DEFAULT_SITE_DIR
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.workflows.daily_pipeline import run_daily_pipeline


def register(app: typer.Typer) -> None:
    @app.command()
    def daily(
        sample_data: bool = typer.Option(False, "--sample-data", help="Use built-in sample data."),
        input_path: Path | None = typer.Option(None, "--input-path", help="Local JSON or CSV signal file."),
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        resources_path: Path = typer.Option(Path("RESOURCES.md"), "--resources-path"),
        brief_path: Path = typer.Option(Path("data/processed/market_brief.md"), "--brief-path"),
        intel_path: Path = typer.Option(DEFAULT_PUBLIC_INTEL_PATH, "--intel-path"),
        site_dir: Path = typer.Option(DEFAULT_SITE_DIR, "--site-dir"),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
        stash_ninja_watchlist: bool = typer.Option(
            False,
            "--stash-ninja-watchlist",
            help="Also write a derived-only local Stash-Ninja companion handoff.",
        ),
        stash_ninja_path: Path = typer.Option(
            DEFAULT_STASH_NINJA_WATCHLIST_PATH,
            "--stash-ninja-path",
        ),
        stash_ninja_markdown_path: Path | None = typer.Option(
            None,
            "--stash-ninja-markdown-path",
        ),
        watch_threshold: float = typer.Option(55.0, "--watch-threshold", min=0, max=100),
        buy_threshold: float = typer.Option(75.0, "--buy-threshold", min=0, max=100),
        big_delta: float = typer.Option(10.0, "--big-delta", min=0, max=100),
    ) -> None:
        alert_settings = daily_alert_settings(watch_threshold, buy_threshold, big_delta)
        source_mode, opportunities = daily_opportunities(sample_data, input_path)
        result = run_daily_pipeline(
            opportunities=opportunities,
            source_mode=source_mode,
            database_path=database_path,
            resources_path=resources_path,
            brief_path=brief_path,
            intel_path=intel_path,
            site_dir=site_dir,
            limit=limit,
            alert_settings=alert_settings,
        )
        stash_ninja_paths: tuple[Path, Path] | None = None
        if result is not None and stash_ninja_watchlist:
            payload = build_stash_ninja_watchlist(
                repository=result.repository,
                run_id=result.run.id,
                limit=limit,
            )
            if payload is not None:
                written_json = write_stash_ninja_watchlist(payload, stash_ninja_path)
                written_markdown = write_stash_ninja_watchlist_markdown(
                    payload,
                    stash_ninja_markdown_path or stash_ninja_path.with_suffix(".md"),
                )
                stash_ninja_paths = (written_json, written_markdown)
        print_daily_result(result, database_path=database_path, limit=limit)
        if stash_ninja_paths is not None:
            typer.echo(f"Stash-Ninja handoff: {stash_ninja_paths[0]}")
            typer.echo(f"Stash-Ninja handoff Markdown: {stash_ninja_paths[1]}")
