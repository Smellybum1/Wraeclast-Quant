from __future__ import annotations

from typing import Iterable

from wraeclast_quant.config.resource_models import Resource
from wraeclast_quant.config.resource_parser_builders import build_resource
from wraeclast_quant.config.resource_parser_text import normalize_key


def parse_table(rows: Iterable[str], section: str) -> list[Resource]:
    row_list = [row for row in rows if row.strip()]
    if len(row_list) < 2:
        return []

    headers = [normalize_key(cell) for cell in _split_table_row(row_list[0])]
    parsed: list[Resource] = []
    for row in row_list[2:]:
        cells = _split_table_row(row)
        if len(cells) != len(headers):
            continue
        data = dict(zip(headers, cells, strict=True))
        if data.get("name") or data.get("url"):
            parsed.append(build_resource(data, section))
    return parsed


def _split_table_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]
