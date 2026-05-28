from __future__ import annotations

from pathlib import Path

import typer

from wraeclast_quant.reports.calibration import (
    build_calibration,
    calibration_review_prompts,
)
from wraeclast_quant.reports.review_guidance import manual_review_handoff_next_action
from wraeclast_quant.reports.stash_ninja_watchlist import (
    build_stash_ninja_watchlist,
    write_stash_ninja_watchlist,
    write_stash_ninja_watchlist_markdown,
)
from wraeclast_quant.workflows.daily_pipeline import DailyPipelineResult


def write_daily_stash_ninja_handoff(
    result: DailyPipelineResult | None,
    *,
    enabled: bool,
    limit: int,
    stash_ninja_path: Path,
    stash_ninja_markdown_path: Path | None,
) -> tuple[Path, Path] | None:
    if result is None or not enabled:
        return None

    payload = build_stash_ninja_watchlist(
        repository=result.repository,
        run_id=result.run.id,
        limit=limit,
    )
    if payload is None:
        return None

    written_json = write_stash_ninja_watchlist(payload, stash_ninja_path)
    written_markdown = write_stash_ninja_watchlist_markdown(
        payload,
        stash_ninja_markdown_path or stash_ninja_path.with_suffix(".md"),
    )
    return written_json, written_markdown


def print_daily_stash_ninja_handoff(
    result: DailyPipelineResult,
    paths: tuple[Path, Path] | None,
) -> None:
    if paths is None:
        return

    typer.echo(f"Stash-Ninja handoff: {paths[0]}")
    typer.echo(f"Stash-Ninja handoff Markdown: {paths[1]}")
    coverage = result.repository.review_coverage_for_run(result.run.id)
    calibration_prompt_count = 0
    if not coverage.unreviewed_recommendations:
        calibration_prompt_count = len(
            calibration_review_prompts(build_calibration(result.repository))
        )
    typer.echo(
        manual_review_handoff_next_action(
            run_id=result.run.id,
            unreviewed_recommendations=coverage.unreviewed_recommendations,
            calibration_prompt_count=calibration_prompt_count,
        )
    )


__all__ = [
    "print_daily_stash_ninja_handoff",
    "write_daily_stash_ninja_handoff",
]
