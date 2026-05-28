from __future__ import annotations

from wraeclast_quant.collectors.pathofexile_currency_exchange_ui_observation_models import (
    CurrencyExchangeUiStockRow,
    RatioValue,
)


def currency_name(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("_", " ").split())


def stock_row_summary(row: CurrencyExchangeUiStockRow) -> str:
    prefix = {"exact": "", "less_than": "<", "greater_than": ">"}[row.comparator]
    return f"{prefix}{format_ratio_value(row.ratio)} stock {row.stock:,}"


def ratio_summary(value: RatioValue | None, no_stock: bool) -> str:
    if no_stock:
        return "No Stock"
    if value is None:
        return "not supplied"
    return format_ratio_value(value)


def format_ratio_value(value: RatioValue) -> str:
    if isinstance(value, str):
        return value
    return f"{value['want']:g}:{value['have']:g}"


def markdown_cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


__all__ = [
    "currency_name",
    "format_ratio_value",
    "markdown_cell",
    "ratio_summary",
    "stock_row_summary",
]
