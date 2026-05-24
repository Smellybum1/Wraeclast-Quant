from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

WATCH_THRESHOLD = 55.0
BUY_THRESHOLD = 75.0
BIG_POSITIVE_DELTA = 10.0

_ACTION_RANK = {
    "AVOID": 0,
    "HOLD / SELL SELECTIVELY": 1,
    "WATCH": 2,
    "BUY": 3,
}


class AlertCandidate(BaseModel):
    item_name: str
    severity: str
    reason: str
    previous_score: float | None = None
    latest_score: float | None = None
    score_delta: float | None = None
    previous_action: str | None = None
    latest_action: str | None = None


class AlertRuleSettings(BaseModel):
    watch_threshold: float = Field(default=WATCH_THRESHOLD, ge=0, le=100)
    buy_threshold: float = Field(default=BUY_THRESHOLD, ge=0, le=100)
    big_positive_delta: float = Field(default=BIG_POSITIVE_DELTA, ge=0, le=100)

    @model_validator(mode="after")
    def validate_threshold_order(self) -> "AlertRuleSettings":
        if self.buy_threshold < self.watch_threshold:
            raise ValueError("buy_threshold must be greater than or equal to watch_threshold")
        return self


__all__ = [
    "BIG_POSITIVE_DELTA",
    "BUY_THRESHOLD",
    "WATCH_THRESHOLD",
    "AlertCandidate",
    "AlertRuleSettings",
]
