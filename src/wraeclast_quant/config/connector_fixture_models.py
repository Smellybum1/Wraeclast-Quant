from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from wraeclast_quant.config.fetch_policy import FetchPlan
from wraeclast_quant.intelligence.scoring import OpportunityInputs


class ConnectorFixtureItem(BaseModel):
    name: str
    category: str = ""
    price_text: str = ""
    confidence: str = ""
    notes: str = ""
    signals: OpportunityInputs | None = None


class ConnectorFixture(BaseModel):
    source_name: str
    generated_at: str
    items: list[ConnectorFixtureItem]


class ConnectorFixtureRunResult(BaseModel):
    fixture: ConnectorFixture | None
    rows: list[ConnectorFixtureItem]
    fetch_plan: FetchPlan | None
    ready: bool
    blockers: list[str]


class ConnectorFixtureExportResult(BaseModel):
    output_path: Path
    item_count: int
    source_name: str
