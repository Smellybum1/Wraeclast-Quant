from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


RatioValue = str | dict[str, float]


class CurrencyExchangeUiStockRow(BaseModel):
    ratio: RatioValue
    stock: int = Field(ge=0)
    comparator: Literal["exact", "less_than", "greater_than"] = "exact"


class CurrencyExchangeUiObservation(BaseModel):
    want_currency: str
    have_currency: str
    market_ratio: RatioValue | None = None
    stock_rows: list[CurrencyExchangeUiStockRow] = Field(default_factory=list)
    no_stock: bool = False
    league: str | None = None
    notes: str = ""


class CurrencyExchangeUiObservationSnapshot(BaseModel):
    league: str
    observed_at: str | None = None
    observations: list[CurrencyExchangeUiObservation]


@dataclass(frozen=True)
class CurrencyExchangeUiObservationExportResult:
    output_path: Path
    item_count: int
    source_name: str
    review_notes_path: Path | None = None
    capture_review_flag_count: int = 0


__all__ = [
    "CurrencyExchangeUiObservation",
    "CurrencyExchangeUiObservationExportResult",
    "CurrencyExchangeUiObservationSnapshot",
    "CurrencyExchangeUiStockRow",
    "RatioValue",
]
