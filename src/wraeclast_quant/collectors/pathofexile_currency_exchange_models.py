from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


class CurrencyExchangeMarket(BaseModel):
    league: str
    market_id: str
    volume_traded: dict[str, int]
    lowest_stock: dict[str, int]
    highest_stock: dict[str, int]
    lowest_ratio: dict[str, int]
    highest_ratio: dict[str, int]


class CurrencyExchangePayload(BaseModel):
    next_change_id: int
    markets: list[CurrencyExchangeMarket]


class CurrencyExchangeManualMarket(BaseModel):
    league: str
    left_currency: str
    right_currency: str
    left_volume_traded: int
    right_volume_traded: int
    left_lowest_stock: int
    right_lowest_stock: int
    left_highest_stock: int
    right_highest_stock: int
    left_lowest_ratio: int
    right_lowest_ratio: int
    left_highest_ratio: int
    right_highest_ratio: int


class CurrencyExchangeManualSnapshot(BaseModel):
    next_change_id: int
    markets: list[CurrencyExchangeManualMarket]


@dataclass(frozen=True)
class CurrencyExchangeMarketObservation:
    league: str
    market_id: str
    next_change_id: int
    volume_total: int
    highest_stock_total: int
    ratio_spread_percent: float


@dataclass(frozen=True)
class CurrencyExchangeBaselineDiagnostics:
    league: str
    market_id: str
    observations: int
    demand_index: float
    liquidity_index: float
    spread_index: float
    freshness_lag_seconds: int
    freshness_status: str
    stale_data_penalty: float
    confidence: str
    blockers: tuple[str, ...] = ()


__all__ = [
    "CurrencyExchangeBaselineDiagnostics",
    "CurrencyExchangeManualMarket",
    "CurrencyExchangeManualSnapshot",
    "CurrencyExchangeMarket",
    "CurrencyExchangeMarketObservation",
    "CurrencyExchangePayload",
]
