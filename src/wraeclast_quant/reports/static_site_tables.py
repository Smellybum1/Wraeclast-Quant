from __future__ import annotations

from html import escape
from typing import Any


def section(title: str, body: str) -> str:
    return "\n".join(
        [
            '    <section class="panel">',
            f"      <h2>{escape(title)}</h2>",
            body,
            "    </section>",
        ]
    )


def key_value_table(rows: list[tuple[str, Any]]) -> str:
    table_rows = [
        f"        <tr><th>{escape(str(key))}</th><td>{escape(str(value))}</td></tr>"
        for key, value in rows
    ]
    return "\n".join(['      <table class="kv">', *table_rows, "      </table>"])


def table(headers: list[str], rows: list[list[Any]], empty_message: str = "No data.") -> str:
    if not rows:
        return f'<p class="empty">{escape(empty_message)}</p>'
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        body_rows.append(
            "        <tr>"
            + "".join(f"<td>{cell if is_html_cell(cell) else escape(str(cell))}</td>" for cell in row)
            + "</tr>"
        )
    return "\n".join(
        [
            "      <table>",
            f"        <thead><tr>{head}</tr></thead>",
            "        <tbody>",
            *body_rows,
            "        </tbody>",
            "      </table>",
        ]
    )


def badge(value: Any) -> str:
    text = escape(str(value))
    return f'<span class="badge">{text}</span>'


def is_html_cell(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.startswith('<span class="badge">')
        and value.endswith("</span>")
    )


__all__ = ["badge", "is_html_cell", "key_value_table", "section", "table"]
