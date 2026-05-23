from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ValidationError

from wraeclast_quant.config.connector_policy import (
    ConnectorPolicyError,
    ConnectorReview,
    check_connector_review,
)
from wraeclast_quant.config.fetch_policy import FetchPlan, build_fetch_plan
from wraeclast_quant.config.resources_loader import Resource
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


def load_connector_fixture(path: str | Path) -> ConnectorFixture:
    fixture_path = Path(path)
    try:
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ConnectorPolicyError(f"Could not read connector fixture: {error}") from error
    except json.JSONDecodeError as error:
        raise ConnectorPolicyError(f"Invalid connector fixture JSON: {error}") from error

    try:
        return ConnectorFixture.model_validate(raw)
    except ValidationError as error:
        raise ConnectorPolicyError(f"Invalid connector fixture: {error}") from error


def run_connector_fixture(
    review: ConnectorReview,
    resources: list[Resource],
    fixture_path: str | Path,
) -> ConnectorFixtureRunResult:
    check = check_connector_review(review, resources)
    if not check.ready:
        return ConnectorFixtureRunResult(
            fixture=None,
            rows=[],
            fetch_plan=None,
            ready=False,
            blockers=check.blockers,
        )

    plan_result = build_fetch_plan(review, resources)
    if plan_result.plan is None:
        return ConnectorFixtureRunResult(
            fixture=None,
            rows=[],
            fetch_plan=None,
            ready=False,
            blockers=plan_result.check.blockers,
        )

    fixture = load_connector_fixture(fixture_path)
    return ConnectorFixtureRunResult(
        fixture=fixture,
        rows=fixture.items,
        fetch_plan=plan_result.plan,
        ready=True,
        blockers=[],
    )


def export_connector_fixture_signals(
    review: ConnectorReview,
    resources: list[Resource],
    fixture_path: str | Path,
    output_path: str | Path,
) -> ConnectorFixtureExportResult:
    result = run_connector_fixture(review, resources, fixture_path)
    if not result.ready:
        blockers = "\n".join(result.blockers)
        raise ConnectorPolicyError(blockers or "Connector fixture export failed.")
    if result.fixture is None:
        raise ConnectorPolicyError("Connector fixture export failed.")

    payload = {"items": connector_fixture_signal_items(result.rows)}

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return ConnectorFixtureExportResult(
        output_path=destination,
        item_count=len(result.rows),
        source_name=result.fixture.source_name,
    )


def connector_fixture_signal_items(
    rows: list[ConnectorFixtureItem],
) -> list[dict[str, object]]:
    missing_signal_items = [item.name for item in rows if item.signals is None]
    if missing_signal_items:
        names = ", ".join(missing_signal_items)
        raise ConnectorPolicyError(
            f"Connector fixture export requires normalized signals for every row. "
            f"Missing signals for: {names}"
        )

    return [
        {
            "name": item.name,
            "signals": item.signals.model_dump() if item.signals is not None else {},
        }
        for item in rows
    ]
