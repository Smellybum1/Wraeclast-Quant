from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from wraeclast_quant.collectors.source_connector import SourceConnector, source_connector_from_review
from wraeclast_quant.commands._connector_support import file_sha256, load_fixture_resources
from wraeclast_quant.config.connector_fixtures import (
    ConnectorFixtureRunResult,
    connector_fixture_signal_items,
    run_connector_fixture,
)
from wraeclast_quant.config.connector_policy import ConnectorPolicyError, ConnectorReview, load_connector_review
from wraeclast_quant.intelligence.opportunity_ranker import rank_opportunities
from wraeclast_quant.intelligence.scoring import ScoredOpportunity
from wraeclast_quant.workflows.daily_pipeline import RunProvenanceInput


@dataclass(frozen=True)
class ConnectorFixtureDailyInput:
    review: ConnectorReview
    connector: SourceConnector
    fixture_result: ConnectorFixtureRunResult
    opportunities: list[ScoredOpportunity]


def load_connector_fixture_daily_input(
    *,
    review_path: Path,
    fixture_path: Path,
    resources_path: Path,
) -> ConnectorFixtureDailyInput:
    review = load_connector_review(review_path)
    connector_resources = load_fixture_resources(resources_path)
    connector = source_connector_from_review(review, connector_resources)
    fixture_result = run_connector_fixture(review, connector_resources, fixture_path)
    if not fixture_result.ready:
        blockers = "\n".join(fixture_result.blockers)
        raise ConnectorPolicyError(blockers or "Connector fixture daily failed.")

    items = connector_fixture_signal_items(fixture_result.rows)
    return ConnectorFixtureDailyInput(
        review=review,
        connector=connector,
        fixture_result=fixture_result,
        opportunities=rank_opportunities(items),
    )


def connector_fixture_daily_provenance(
    *,
    daily_input: ConnectorFixtureDailyInput,
    review_path: Path,
    fixture_path: Path,
) -> RunProvenanceInput:
    assert daily_input.fixture_result.fixture is not None
    return RunProvenanceInput(
        source_kind="connector-fixture",
        resource_name=daily_input.connector.resource.name,
        connector_id=daily_input.connector.connector_id,
        access_method=daily_input.review.access_method,
        metadata={
            "connector_class": daily_input.connector.__class__.__name__,
            "fixture_source_name": daily_input.fixture_result.fixture.source_name,
            "fixture_generated_at": daily_input.fixture_result.fixture.generated_at,
            "fixture_item_count": len(daily_input.fixture_result.rows),
            "review_file": review_path.name,
            "review_sha256": file_sha256(review_path),
            "fixture_file": fixture_path.name,
            "fixture_sha256": file_sha256(fixture_path),
            "future_cache_path": str(daily_input.connector.fetch_plan.cache_path),
        },
    )


__all__ = [
    "ConnectorFixtureDailyInput",
    "connector_fixture_daily_provenance",
    "load_connector_fixture_daily_input",
]
