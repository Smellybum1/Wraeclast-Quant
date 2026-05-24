from __future__ import annotations


def run_label(run_id: int | None) -> str:
    return f"#{run_id}" if run_id is not None else "none"


def markdown_cell(value: str) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def markdown_value(value: str) -> str:
    normalized = " ".join(str(value).split())
    return normalized or "None"


__all__ = [
    "markdown_cell",
    "markdown_value",
    "run_label",
]
