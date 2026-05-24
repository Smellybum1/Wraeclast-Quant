from __future__ import annotations

import json
from pathlib import Path

from wraeclast_quant.config.connector_fixture_models import (
    ConnectorFixtureExportResult,
    ConnectorFixtureItem,
)
from wraeclast_quant.config.connector_fixture_runner import run_connector_fixture
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview
from wraeclast_quant.config.resources_loader import Resource


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
