from __future__ import annotations

from pathlib import Path

import typer

MAX_REVIEW_CONTEXT_BYTES = 64 * 1024


def read_review_queue_context(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_REVIEW_CONTEXT_BYTES:
            raise typer.BadParameter(
                f"review context is too large; limit is {MAX_REVIEW_CONTEXT_BYTES} bytes"
            )
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise typer.BadParameter(f"could not read review context: {error}") from error


__all__ = ["MAX_REVIEW_CONTEXT_BYTES", "read_review_queue_context"]
