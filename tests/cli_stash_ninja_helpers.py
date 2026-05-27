from __future__ import annotations

from pathlib import Path


def stash_ninja_args(
    database_path: Path,
    output_path: Path,
    markdown_output_path: Path | None = None,
    run_id: int | None = None,
    limit: int | None = None,
    min_score: float | None = None,
) -> list[str]:
    args = [
        "stash-ninja-watchlist",
        "--database-path",
        str(database_path),
        "--output-path",
        str(output_path),
    ]
    if markdown_output_path is not None:
        args.extend(["--markdown-output-path", str(markdown_output_path)])
    if run_id is not None:
        args.extend(["--run-id", str(run_id)])
    if limit is not None:
        args.extend(["--limit", str(limit)])
    if min_score is not None:
        args.extend(["--min-score", str(min_score)])
    return args


__all__ = ["stash_ninja_args"]
