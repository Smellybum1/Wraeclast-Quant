from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wraeclast_quant.reports.review_queue_worksheet import review_queue_worksheet_command
from wraeclast_quant.reports.stash_ninja_watchlist import (
    DEFAULT_STASH_NINJA_WATCHLIST_PATH,
    build_stash_ninja_watchlist,
    write_stash_ninja_watchlist,
    write_stash_ninja_watchlist_markdown,
)
from wraeclast_quant.storage.db import DEFAULT_DATABASE_PATH
from wraeclast_quant.storage.repositories import SnapshotRepository

console = Console(width=260)


def register(app: typer.Typer) -> None:
    @app.command("stash-ninja-watchlist")
    def stash_ninja_watchlist(
        database_path: Path = typer.Option(DEFAULT_DATABASE_PATH, "--database-path"),
        run_id: int | None = typer.Option(None, "--run-id", min=1),
        limit: int = typer.Option(10, "--limit", min=1, max=50),
        min_score: float = typer.Option(55.0, "--min-score", min=0, max=100),
        output_path: Path = typer.Option(
            DEFAULT_STASH_NINJA_WATCHLIST_PATH,
            "--output-path",
        ),
        markdown_output_path: Path | None = typer.Option(None, "--markdown-output-path"),
    ) -> None:
        payload = build_stash_ninja_watchlist(
            repository=SnapshotRepository(database_path),
            run_id=run_id,
            limit=limit,
            min_score=min_score,
        )
        if payload is None:
            if run_id is None:
                console.print("No snapshots found.")
            else:
                console.print(f"Analysis run #{run_id} was not found.")
            return

        written_json = write_stash_ninja_watchlist(payload, output_path)
        written_markdown = write_stash_ninja_watchlist_markdown(
            payload,
            markdown_output_path or output_path.with_suffix(".md"),
        )
        console.print(
            "Wrote derived-only Stash-Ninja companion watchlist "
            f"for run #{payload['latest_run']['id']} to {written_json}"
        )
        console.print(f"Wrote manual handoff Markdown to {written_markdown}")
        console.print("Manual application required; no Exile-UI files or game-client state were touched.")
        console.print(f"Next: {review_queue_worksheet_command(int(payload['latest_run']['id']))}")
